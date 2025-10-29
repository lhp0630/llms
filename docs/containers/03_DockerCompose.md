概述
---

- [简介](#简介)
- [安装](#安装)
- [Composefile](#composefile)
  - [拉取镜像运行服务](#拉取镜像运行服务)
  - [构建镜像运行服务](#构建镜像运行服务)
  - [指定镜像名称](#指定镜像名称)
  - [指定 Composefile](#指定-composefile)
- [命令](#命令)
  - [启动项目](#启动项目)
  - [停止项目](#停止项目)
  - [列出项目所有的服务](#列出项目所有的服务)
  - [查看服务的日志](#查看服务的日志)
  - [进入到服务中](#进入到服务中)
  - [启动服务](#启动服务)
  - [重新启动服务](#重新启动服务)
  - [停止正在运行的服务](#停止正在运行的服务)
  - [暂停服务](#暂停服务)
  - [恢复服务](#恢复服务)
  - [删除服务](#删除服务)
  - [构建项目](#构建项目)
- [卷](#卷)
  - [具体路径](#具体路径)
  - [具名卷](#具名卷)
- [网络](#网络)

简介
---

Docker Compose 是 Docker 官方的多容器应用编排工具，用于通过一个配置文件定义和管理多个容器服务，配置文件通常被命名为 `docker-compose.yml`。

安装
---

```sh
sudo apt update
sudo apt install docker-compose-plugin
```

检查 Docker Compose 是否成功安装

```sh
docker compose version
```

> 该安装方式需要系统中已经安装好了 Docker，`docker compose` 命令是 Docker Compose v2 版本，是 Docker 官方推荐的版本，它作为 Docker CLI 插件集成在 `docker` 命令中，而不是独立的 docker compose 二进制程序。

Composefile
---

### 拉取镜像运行服务

这是一个简单的 Minio 服务 `docker-compose.yml` 配置文件: 
```yml
services:
  minio:
    image: docker.io/minio/minio:latest
    command: minio server /minio_data --console-address ":9001"
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
```

关键参数深度解析:
- `services`: 定义应用中的各个组件。在一个文件中可以定义多个服务（如 MinIO + 数据库），它们会自动加入同一个网络。
- `image`: 告诉 Docker 从哪里下载镜像。
- `command`: 覆盖容器启动后执行的命令。
- `environment`: 配置容器内的运行环境。对于 MinIO 来说，这是设置初始用户名和密码的地方。
- `ports`: 端口映射。MinIO 需要两个端口: `9000` 用于程序调用，`9001` 用于你在浏览器中操作的 UI 界面。

运行 Docker Compose 项目: 
```sh
docker compose up
```

`up -d` 可在后台运行。

停止容器但保留数据卷: 
```sh
docker compose stop
```

停止并移除容器及网络: 
```sh
docker compose down
```

### 构建镜像运行服务

编写 `Dockerfile` 文件: 
```docker
FROM node:14.18.1 AS build
WORKDIR /source
COPY . .
RUN yarn install \
    && npm run build

FROM node:14.18.1-alpine
WORKDIR /app
COPY --from=build /source/dist .
COPY --from=build /source/node_modules node_modules
ENTRYPOINT [ "node", "main" ]
```

编写 `docker-compose.yml` 文件: 

```yml
services: 
  app:
    build: .
    ports:
      - "3000:3000"
```

构建并运行 Docker Compose 项目: 
```sh
docker compose up --build
```

### 指定镜像名称

```yml
services: 
  app:
    build: .
    image: myapp:latest
    ports:
      - "3000:3000"
```

### 指定 Composefile

```yml
services: 
  app:
    build:
      context: .
      dockerfile: Default_Dockerfile
    ports:
      - "3000:3000"
```

命令
---

### 启动项目

自动构建镜像、创建网络、创建并启动服务: 

```sh
docker compose up
```

后台运行: 

```sh
docker compose up -d
```

指定 Docker Compose 配置文件: 

```sh
docker compose -f docker-compose.production.yml up
```

指定服务: 

```sh
docker compose up nginx
```

重新构建: 

```sh
docker compose up --build
```

### 停止项目

停止并删除网络、服务。

```sh
docker compose down
```

### 列出项目所有的服务

```sh
docker compose ps
```

### 查看服务的日志

```sh
docker compose logs nginx
```

`-f` 监听服务的输出

```sh
docker compose logs nginx -f
```

### 进入到服务中

```sh
docker compose exec nginx bash
```

### 启动服务

```sh
docker compose start nginx
```

### 重新启动服务

```sh
docker compose restart nginx
```

### 停止正在运行的服务

```sh
docker compose stop nginx
```

### 暂停服务

```sh
docker compose pause nginx
```

### 恢复服务

```sh
docker compose unpause nginx
```

### 删除服务

```sh
docker compose rm nginx
```

### 构建项目

```sh
docker compose build
```

指定服务

```sh
docker compose build nginx
```

`--no-cache` 不使用缓存

```sh
docker compose build --no-cache
```

卷
---

### 具体路径

由自己决定容器运行时所需的数据存储在宿主机的具体位置，如下列示例中展示宿主机路径 `/data/myapp`，将该路径的数据挂到容器文件系统中。

```yml
services:
  myapp:
    image: myapp
    volumes:
      - /data/myapp:/app/data
    ports:
      - "8000:8000"
```

### 具名卷

由 Docker 自动管理（通常在 `/var/lib/docker/volumes/`），对比具体路径优势是跨平台性，可以有效避免不同系统的文件权限体系，隔离性，宿主机数据不易误删。

```yml
services:
  myapp:
    image: myapp
    volumes:
      - myapp:/app/data
    ports:
      - "8000:8000"

volumes:
  myapp:
```

网络
---

- **主机网络模式**

  该模式下，容器与宿主机之间没有网络隔离。例如你在容器内运行一个监听 `3000` 端口的服务，它会直接占用宿主机的 `3000` 端口。
  
  它的网络性能最高，因为没有网络地址转换（NAT）的开销。适用于需要处理大量并发连接或容器需要操作宿主机的特定网络协议栈。
  
  ```yml
  services:
    app:
      build: .
      image: myapp
      network_mode: host
  ```

- **桥接网络模式**

  该模式是 Docker 的默认网络行为，容器拥有独立的内部 IP 地址，运行在沙盒化的网络环境中。容器端口默认不暴露给宿主机，除非你使用 `ports` 映射。

  适用于需要保护组件实现网络隔离，不让外界直接访问或组件之间隔离网络。该模式也运用于标准的微服务架构。

  ```yml
  services:
    app:
      build: .
      image: myapp
      networks:
        default:
          aliases:
            - server
  
  networks:
    default:
  ```

  - `aliases`：设置该组件的别名，即通过 `server` 这个别名，使同一网络内的其他容器可以通过 `http://server` 访问到这个容器，而不需要知道它的具体 IP。
