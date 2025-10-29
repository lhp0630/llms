# Nginx

- [配置模板](#配置模板)
- [访问控制](#访问控制)
  - [匹配 URL 路径前缀](#匹配-url-路径前缀)
  - [配置虚拟路径](#配置虚拟路径)
- [重写 HTTP 请求](#重写-http-请求)
  - [重写请求方法](#重写请求方法)
  - [重写请求头](#重写请求头)
- [重写 HTTP 响应](#重写-http-响应)
  - [添加响应头](#添加响应头)
  - [移除响应头](#移除响应头)
- [扩展](#扩展)
  - [启用 CORS 跨域](#启用-cors-跨域)
  - [处理 OPTIONS 方法的请求](#处理-options-方法的请求)
  - [限制使用 “安全” 的 HTTP 请求](#限制使用-安全-的-http-请求)
  - [WebSocket](#websocket)
- [Docker](#docker)
- [Docker-Compose](#docker-compose)
- [Kubernetes](#kubernetes)
  - [代理 Pod](#代理-pod)

## 配置模板

```
#user  nobody;
worker_processes  1;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;

    keepalive_timeout  65;

    #gzip  on;

    server {
        listen       80;
        server_name  localhost;

        #charset koi8-r;

        location / {
            root   html;
            index  index.html index.htm;
        }

        #error_page  404              /404.html;
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
    }
}
```

## 访问控制

### 匹配 URL 路径前缀

```conf
# 匹配 /api 前缀开始的 HTTP 请求发送到 localhost:5000
# 其他则访问静态页面

server {
    listen       80;
    server_name  localhost;

    location /api {
        proxy_pass http://localhost:5000/api;
    }

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }
}
```

### 配置虚拟路径

```conf
server {
    listen       80;
    server_name  localhost;

    location /document {
        alias  /usr/share/nginx/html/doc;
        autoindex on;
    }
}
```

## 重写 HTTP 请求

### 重写请求方法

使用 `set-method` 配置指令重写请求的方法。

```conf
# 将 PUT 方法的请求更改为 POST 方法

location / {
    if ($request_method = PUT) {
        proxy_method POST;
    }

    proxy_pass http://localhost:5000;
}
```

### 重写请求头

使用 `proxy_set_header` 配置指令添加请求头。

```conf
# 判断请求头中是否存在 X-Forwarded-For
# 如果不存在则添加包含客户端地址的 X-Forwarded-For 请求头

location / {
    if ($http_x_forwarded_for) {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    proxy_pass http://localhost:5000;
}
```

## 重写 HTTP 响应

### 添加响应头

使用 `add_header` 配置指令添加响应头。默认情况下，当响应状态码为 `200, 201, 204, 206, 301, 302, 303, 304, 307, 308` 时， `add_header` 可将指定字段添加到响应头。

```conf
location / {
    add_header X-Powered-By "WebServer";

    proxy_pass http://localhost:5000;
}
```

当指定为 `always` 时，则始终都会将指定字段添加到响应头。

```conf
location / {
    add_header X-Powered-By "WebServer" always;

    proxy_pass http://localhost:5000;
}
```

### 移除响应头

使用 `proxy_hide_header` 配置指令移除响应头。

```conf
location / {
    proxy_hide_header Cookie;

    proxy_pass http://localhost:5000;
}
```

## 扩展

### 启用 CORS 跨域

```conf
location / {
    add_header Access-Control-Allow-Origin $http_origin;
    add_header Access-Control-Allow-Methods *;
    add_header Access-Control-Allow-Headers *;

    proxy_pass http://localhost:5000;
}
```

### 处理 OPTIONS 方法的请求

```conf
location / {
    if ($request_method = OPTIONS) {
        add_header Access-Control-Allow-Origin $http_origin;
        add_header Access-Control-Allow-Methods *;
        add_header Access-Control-Allow-Headers *;
        add_header Access-Control-Max-Age 1728000;
        return 204;
    }

    proxy_pass http://localhost:5000;
}
```

### 限制使用 “安全” 的 HTTP 请求

```conf
location / {
    if ($request_method !~ ^(GET|POST|HEAD|OPTIONS)$ ) {
        return 405;
    }
    set $proxy_request_method $request_method;
    if ($http_x_http_method_override){
        set $proxy_request_method $http_x_http_method_override;
    }
    proxy_set_header X-Http-Method-Override "";
    proxy_method $proxy_request_method;

    proxy_pass http://localhost:5000;
}
```

### WebSocket

```conf
location / {
    set $proxy_connection close;
    if ($http_connection ~ "Upgrade") {
        set $proxy_connection $http_connection;
    }
    proxy_set_header Connection $proxy_connection;
    proxy_set_header Upgrade $http_upgrade;

    proxy_pass http://localhost:5000;
}
```

## Docker

拉取 Nginx 镜像：

```bash
docker pull nginx
```

运行 Nginx 容器：

```bash
docker run \
  -v ./nginx.conf:/etc/nginx/nginx.conf:ro \
  -v ./web/content:/usr/share/nginx/html:ro \
  -p 80:80 \
  nginx
```

- `-v ./nginx.conf:/etc/nginx/nginx.conf:ro` 是将 `./nginx.conf` 文件挂载到容器的 `/etc/nginx/nginx.conf` 路径下，并设置为只读模式
- `-v ./web/content:/usr/share/nginx/html:ro` 是将 `./web/content` 文件夹挂载到容器的 `/usr/share/nginx/html` 路径下，并设置为只读模式
- `-p 80:80` 是将容器的 80 端口映射到主机的 80 端口

## Docker-Compose

编辑 `docker-compose.yml` 文件，配置 Nginx 服务：

```yaml
version: "3"
services:

  proxy:
    image: nginx:latest
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./web/content:/usr/share/nginx/html:ro
    ports:
      - "80:80"
    restart: always
```

- `./nginx.conf:/etc/nginx/nginx.conf:ro` 是将 `./nginx.conf` 文件挂载到容器的 `/etc/nginx/nginx.conf` 路径下，并设置为只读模式
- `./web/content:/usr/share/nginx/html:ro` 是将 `./web/content` 目录挂载到容器的 `/usr/share/nginx/html` 路径下，并设置为只读模式
- `80:80` 是将容器的 80 端口映射到主机的 80 端口

运行 Nginx 服务：

```bash
docker-compose up -d
```

## Kubernetes

### 代理 Pod

运行 `kubectl get pod --all-namespaces` 将 Pod 查询出来：

```bash
kubectl get pod --all-namespaces

NAMESPACE                 NAME                                                       READY   STATUS             RESTARTS   AGE
default                   minio-86687bcc49-4w89n                                     1/1     Running            3          248d
default                   mysql-6658cddcd9-khb82                                     1/1     Running            3          267d
default                   redis-6985769965-6wfnq                                     1/1     Running            3          248d
kube-system               coredns-558bd4d5db-khr5n                                   1/1     Running            21         281d
kube-system               coredns-558bd4d5db-wh5vw                                   1/1     Running            21         281d
kube-system               etcd-k8s-master                                            1/1     Running            21         281d
kube-system               kube-apiserver-k8s-master                                  1/1     Running            27         281d
kube-system               kube-controller-manager-k8s-master                         1/1     Running            32         281d
kube-system               kube-flannel-ds-745vw                                      1/1     Running            23         281d
kube-system               kube-flannel-ds-mwxmz                                      1/1     Running            3          267d
kube-system               kube-flannel-ds-wqcl7                                      1/1     Running            22         281d
kube-system               kube-proxy-5dr6l                                           1/1     Running            21         281d
kube-system               kube-proxy-khxst                                           1/1     Running            21         281d
kube-system               kube-proxy-pkgmw                                           1/1     Running            3          267d
kube-system               kube-scheduler-k8s-master                                  1/1     Running            30         281d
kubernetes-dashboard      dashboard-metrics-scraper-856586f554-lsgft                 1/1     Running            14         280d
kubernetes-dashboard      kubernetes-dashboard-78c79f97b4-zg9cq                      1/1     Running            13         280d
report                    report-helm-chart-6f475cbfcc-7nzkk                         1/1     Running            0          8h
```

接下来配置 Nginx 的代理，代理的地址填写 Pod 的 DNS 条目：

```bash
location /api {
    proxy_pass http://report-helm-chart.report.svc.cluster.local:80/api;
}
```

> DNS 条目的形式是 `NAME.NAMESPACE.svc.cluster.local`
