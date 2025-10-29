概述
---

- [简介](#简介)
  - [为什么要使用 Docker ？](#为什么要使用-docker-)
  - [Docker 对比虚拟机的优势？](#docker-对比虚拟机的优势)
- [安装](#安装)
- [使用镜像](#使用镜像)
  - [查看镜像](#查看镜像)
    - [列出本地镜像](#列出本地镜像)
    - [查看详细信息](#查看详细信息)
    - [查看历史记录](#查看历史记录)
  - [搜索镜像](#搜索镜像)
  - [拉取镜像](#拉取镜像)
  - [删除和清理镜像](#删除和清理镜像)
    - [删除镜像](#删除镜像)
    - [清理镜像](#清理镜像)
  - [保存和载入镜像](#保存和载入镜像)
    - [保存镜像](#保存镜像)
    - [载入镜像](#载入镜像)
  - [导入镜像](#导入镜像)
  - [标记镜像](#标记镜像)
  - [登录镜像注册中心](#登录镜像注册中心)
  - [推送镜像](#推送镜像)
- [操作容器](#操作容器)
  - [查看容器](#查看容器)
    - [列出所有容器](#列出所有容器)
    - [查看容器详情](#查看容器详情)
    - [查看容器内进程](#查看容器内进程)
    - [查看统计信息](#查看统计信息)
  - [创建与启动容器](#创建与启动容器)
    - [新建容器](#新建容器)
    - [启动容器](#启动容器)
    - [新建并启动容器](#新建并启动容器)
    - [重新启动容器](#重新启动容器)
  - [停止容器](#停止容器)
    - [暂停容器](#暂停容器)
    - [终止容器](#终止容器)
  - [删除和清理容器](#删除和清理容器)
    - [删除容器](#删除容器)
    - [清理容器](#清理容器)
  - [查看容器运行日志](#查看容器运行日志)
  - [进入容器](#进入容器)
    - [Attach 指令](#attach-指令)
    - [Exec 指令](#exec-指令)
  - [导出容器](#导出容器)
  - [将容器保存为新的镜像](#将容器保存为新的镜像)
  - [拷贝容器中的文件](#拷贝容器中的文件)
  - [更新容器的配置](#更新容器的配置)
- [构建](#构建)
  - [多阶段构建](#多阶段构建)
- [网络](#网络)
  - [列出所有网络](#列出所有网络)
  - [创建网络](#创建网络)
  - [删除网络](#删除网络)
  - [容器互联](#容器互联)
  - [使用主机网络](#使用主机网络)
- [其他命令](#其他命令)
  - [查看磁盘使用情况](#查看磁盘使用情况)
  - [清理磁盘](#清理磁盘)
  - [清理镜像](#清理镜像-1)
  - [清理构建缓存](#清理构建缓存)

简介
---

### 为什么要使用 Docker ？

Docker 技术解决了应用的打包与交付问题，提供了只需一次打包，即可到处运行的解决方案。具有以下优势：

- 更快速的交付和部署
- 更轻松的迁移和扩展
- 更高效的资源利用
- 更简单的更新管理

### Docker 对比虚拟机的优势？

- 容器的启动和停止更快
- 容器对系统资源需求更少
- 通过镜像仓库非常方便的获取、分发、更新和存储
- 通过 Dockerfile 实现自动化部署

安装
---

Debian/Ubuntu:

```sh
sudo apt install docker
```

确认 Docker 服务启动正常
```sh
sudo systemctl enable docker
sudo systemctl start docker
```

**Docker 后续环境配置**

- **让你在运行 Docker 命令时，不再需要输入 sudo**

  > 该步骤仅在非 root 用户时需要配置，root 用户无需配置即可直接使用 `docker <cmd>` 进行操作。

  建立 Docker 用户组:
  ```sh
  sudo groupadd docker
  ```
  
  将当前用户加入 Docker 组:
  ```sh
  sudo usermod -aG docker $USER
  ```

  执行完这两行命令后，你的权限并不会立即更新。你需要执行 `newgrp docker` 刷新当前终端会话的组权限。

  > 将用户加入 docker 组在权限上等同于授予了 root 权限。因为拥有 Docker 控制权的用户可以轻易挂载宿主机根目录并修改系统文件。请只对信任的用户执行此操作。

- **镜像加速**

  > 可选步骤，如果访问 Docker 网络比较慢，可以配置访问国内运营商提供的镜像仓库，以加快镜像拉取的时间。

  修改 `/etc/docker/daemon.json` 文件，在 `registry-mirrors` 中加入镜像市场：
  ```sh
  {
    "registry-mirrors": [
      "http://f1361db2.m.daocloud.io"
    ]
  }
  ```
  
  重启 Docker 服务
  ```sh
  sudo systemctl daemon-reload
  sudo systemctl restart docker
  ```
  
  执行 `info` 指令可以检查配置是否生效：
  ```sh
  docker info
  ```
  
  在输出中找到 `Registry`: 
  ```sh
  Server:
    Registry: http://f1361db2.m.daocloud.io
  ```

<details>
  <summary>如果是 Snap 安装 Docker 请改用以下步骤</summary>

  如果 Docker 是通过 Snap 安装的，`daemon.json` 所在位置会有所不同。

  修改 `/var/snap/docker/current/config/daemon.json` 文件，在 `registry-mirrors` 中加入镜像市场：
  ```sh
  {
    "registry-mirrors": [
      "http://f1361db2.m.daocloud.io"
    ]
  }
  ```
  
  重启 Docker 服务
  ```sh
  sudo snap restart docker
  ```
  
  执行 `info` 指令可以检查配置是否生效：
  ```sh
  docker info
  ```
  
  在输出中找到 `Registry`: 
  ```sh
  Server:
    Registry: http://f1361db2.m.daocloud.io
  ```
</details>

使用镜像
---

### 查看镜像

#### 列出本地镜像

```sh
docker images
```

- `-a` 列出所有镜像
- `-f` 过滤镜像，例如：`-f name=nginx`
- `-q` 仅输出 ID 信息

> 更多命令可以通过 `man docker-images` 查看

#### 查看详细信息

```sh
docker inspect nginx
```

#### 查看历史记录

```sh
docker history nginx
```

### 搜索镜像

```sh
docker search nginx
```

- `-f` 过滤镜像，例如：`-f stars=10`
- `--limit` 限制输出结果个数

### 拉取镜像

```sh
docker pull nginx
```

拉取指定标签的镜像：

```sh
docker pull nginx:stable-alpine
```

### 删除和清理镜像

#### 删除镜像

```sh
docker rmi nginx
```

`-f` 强制删除镜像

删除所有镜像:

```sh
docker rmi $(docker images -q)
```

### 保存和载入镜像

#### 保存镜像

```sh
docker save -o nginx.tar nginx
```

使用 `>` 保存镜像

```sh
docker save nginx > nginx.tar
```

保存镜像时压缩包的体积

```sh
docker save nginx | gzip > nginx.tar
```

#### 载入镜像

```sh
docker load -i nginx.tar
```

使用 `<` 载入镜像

```sh
docker load < nginx.tar
```

### 导入镜像

```sh
docker import nginx.tar nginx
```

### 标记镜像

```sh
docker tag nginx nginx:custom
```

### 登录镜像注册中心

```sh
docker login
```

登录到指定镜像注册中心：

```sh
docker login http://192.168.10.229
```

- `-u` 指定账号
- `-p` 指定密码

```sh
docker login http://192.168.10.229 -u admin -p 123456
```

### 推送镜像

```sh
docker push drawmoon/nginx
```

操作容器
---

### 查看容器

#### 列出所有容器

```sh
docker ps
```

- `-a` 包含终止的容器
- `-q` 仅输出 ID 信息
- `-f` 过滤列出的容器，例如：`-f status=exited`

#### 查看容器详情

```sh
docker container inspect some-nginx
```

#### 查看容器内进程

指令效果与 Linux 下 `top` 命令类似，包括 PID 等信息

```sh
docker top some-nginx
```

#### 查看统计信息

通过 `stats` 指令可查看容器的 CPU、内存、存储、网络等情况的统计信息

```sh
docker stats some-nginx
```

### 创建与启动容器

#### 新建容器

```sh
docker create nginx
```

- `-p` 指定端口映射，映射一个端口到内部容器开放的网络端口，例如：`-p 3000:3000`
- `--name` 指定容器的名称，例如：`--name some-nginx`
- `-d` 标记容器为后台运行
- `-e` 指定环境变量，例如：`-e ENV=xxx`
- `-it` 以交互模式运行容器，例如：`-it nginx bash`
- `--entrypoint` 镜像指定了 `ENTRYPOINT` 时，覆盖入口命令，例如：`-it --entrypoint bash nginx`
- `-v` 挂载主机上的文件卷到容器内，例如：`-v /conf/nginx.conf:/etc/nginx/nginx.conf`
- `--restart` 指定容器退出时的重新启动策略，分别为：`no`、`always` 和 `on-failure`，例如：`--restart=always`

> Windows 下挂载文件卷：`-v //D/nginx.conf:/etc/nginx/nginx.conf`

#### 启动容器

```sh
docker start some-nginx
```

#### 新建并启动容器

```sh
docker run nginx
```

> `run` 命令实际上是执行了 `create` 和 `start` 命令， 在执行 `run` 命令时，同样也可以使用 `create` 的子命令。

#### 重新启动容器

```sh
docker restart some-nginx
```

### 停止容器

#### 暂停容器

```sh
docker pause some-nginx
```

#### 终止容器

```sh
docker stop some-nginx
```

### 删除和清理容器

#### 删除容器

```sh
docker rm some-nginx
```

- `-f` 强制删除
- `-l` 删除容器的连接，但不会删除容器
- `-v` 删除容器挂载的数据卷

#### 清理容器

```sh
docker container prune
```

### 查看容器运行日志

```sh
docker logs some-nginx
```

- `--follow (-f)` 监听容器的输出，例如：`docker logs --follow some-nginx`
- `--tail` 从日志末尾显示的行数（默认值为“全部”），例如：`docker logs --tail 100 some-nginx`

### 进入容器

#### Attach 指令

```sh
docker attach some-nginx
```

`--detach-keys` 指定退出 `attach` 的快捷键，默认是 `Ctrl p Ctrl q`

#### Exec 指令

`exec` 是比 `attach` 更方便的指令，可以在不影响容器内的应用情况下，打开一个新的交互界面

```sh
docker exec -it some-nginx bash
```

- `-d` 在容器中后台执行命令
- `-e` 指定环境变量
- `-it` 以交互模式进入容器
- `-u` 设置执行命令的用户
- `--privileged` 分配最高权限，例如：`--privileged=true`
- `--detach-keys` 指定退出 `exec` 的快捷键

### 导出容器

导出后的本地文件，再次通过 `import` 导入为新的镜像，相比 `save`，`export` 指令只会导出当时容器的状态，不包含元数据和历史记录信息

```sh
docker export -o nginx.tar some-nginx
```

使用 `>` 导出容器

```sh
docker export some-nginx > nginx.tar
```

### 将容器保存为新的镜像

```sh
docker commit some-nginx drawmoon/nginx
```

`-m` 可以指定信息，例如：`-m "Commit Message"`

### 拷贝容器中的文件

```sh
docker cp some-nginx:/app/myapp .
```

### 更新容器的配置

```sh
docker update --restart=always some-nginx
```

构建
---

这是一个简单的构建 NodeJS 后台服务 `Dockerfile` 配置文件: 
```
FROM node
WORKDIR /app
COPY . .
RUN npm install \
  && npm run build
ENTRYPOINT ["node", "dist/main"]
```

关键参数深度解析:
- `FROM`: 指定基础镜像
- `WORKDIR`: 指定工作目录
- `COPY`: 复制文件
- `ADD`: 更高级的复制命令，支持 URL
- `ARG`: 定义构建镜像时使用的变量
- `ENV`: 设置环境变量，示例：`ENV k1=v1 k2=v2`
- `RUN`: 构建镜像时运行的命令
- `EXPOSE`: 指定暴露的端口
- `USER`: 指定执行后续命令的用户和用户组
- `CMD`: 容器启动时执行的命令
- `ENTRYPOINT`: 类似 CMD，与 CMD 不同的是不会被 `docker run` 中的命令给覆盖，如果想要覆盖必须配合 `--entrypoint` 参数

> 如果同时设置了 `ENTRYPOINT` 和 `CMD`，当两个参数的值都是数组时，会拼接成一个命令，否则执行 `ENTRYPOINT` 中的命令

**DockerIgnore**

在实际情况下，通常会存在希望构建时不要将某些目录或文件拷贝至镜像中，Docker 提供了一种方式可以配置忽略拷贝的目录或文件。

在 `Dockerfile` 相同的目录位置，创建名称为 `.dockerignore` 的文件。

例如告诉 Docker 在构建过程中不要拷贝 `.git`、`node_modules` 目录:
```
.git
node_modules
```

如果希望忽略某个目录，但同时希望保留该目录下的某一个文件时，可以如下配置:
```
raw
!raw/include.txt
```

**开始构建 Docker 镜像**

在当前工作目录中，通常情况下是 Dockerfile 所在的位置，这也是常见的项目目录结构，执行以下命令:
```sh
docker build -t myapp .
```

关键参数深度解析:
- `.` 表示当前工作目录。
- `-f` 可以指定 Dockerfile 文件，例如 `docker build -t myapp -f Dockerfile.custom .`

### 多阶段构建

为何要使用多阶段构建？
- 减少重复劳动
- 保护源代码
- 降低镜像体积

```docker
FROM node AS build
WORKDIR /source
COPY . .
RUN npm install \
    && npm run build

FROM node
WORKDIR /app
COPY --from=build /source/dist .
COPY --from=build /source/node_modules node_modules
ENTRYPOINT [ "node", "main" ]
```

网络
---

网络服务是 Docker 提供的一种容器互联的方式。

### 列出所有网络

```sh
docker network ls
```

### 创建网络

```sh
docker network create <网络>
```

`-d` 可以指定网络的类型，分别有 `bridge`、`overlay`。

```sh
docker network create -d bridge <网络>
```

### 删除网络

```sh
docker network rm <网络>
```

### 容器互联

`--network` 将容器连接到 `my-network` 网络。

```sh
docker run --network my-network --name pg-server -d postgres

docker run --network my-network --name my-web -e DB_HOST=pg-server -d web
```

### 使用主机网络

```sh
docker run --net=host --name someapp -d myapp
```

其他命令
---

### 查看磁盘使用情况

```sh
docker system df
```

### 清理磁盘

删除关闭的容器、无用的数据卷、网络和构建缓存

```sh
docker system prune
```

#### 清理镜像

`prune` 可以清理临时镜像和没有被使用过的镜像

```sh
docker image prune
```

- `-a` 清理没有在使用的镜像
- `-filter` 过滤镜像
- `-f` 强制删除镜像

### 清理构建缓存

```sh
docker builder prune
```
