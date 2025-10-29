简介
---

Podman 完全兼容 Docker 命令，Podman 几乎是开箱即用的，并且可以像使用 Docker 一样使用 Podman，例如: `podman images`。

Podman vs Docker:

- 无需进程守护
- 无需 Root 权限，原生支持 Rootless 普通用户即可运行
- CLI 直接调用 runc
- 支持将多个容器组合成 Pod（类似 Kubernetes）

Podman 默认不支持镜像名称的简写，需要全名称，例如：

```sh
podman pull docker.io/library/alpine
podman pull docker.io/library/alpine:3.19
```

安装
---

Debian/Ubuntu:

```sh
sudo apt install podman
```

Homebrew:

```sh
brew install podman
```

**配置镜像加速**

> 可选步骤，如果访问 Docker 网络比较慢，可以配置访问国内运营商提供的镜像仓库，以加快镜像拉取的时间。

创建 `registries.conf` 配置文件:
```sh
mkdir -p ~/.config/containers
vim ~/.config/containers/registries.conf
```

填入如下内容:
```toml
unqualified-search-registries = ["docker.io", "quay.io"]

[[registry]]
prefix = "docker.io"
location = "f1361db2.m.daocloud.io"
```

**解决挂载传播警告**

当你作为普通用户运行 Podman 时，Podman 会创建一个属于你的用户命名空间执  行 podman 命令时，系统可能会提示 `WARN[0000] "/" is not a shared   mount, this could cause issues or missing mounts with rootless   containers`。

这是因为宿主机的根目录默认挂载属性为 `private`，在 Rootless 模式下，  Podman 需要根路径为 `shared`，以便在容器命名空间和宿主机之间同步挂载点。

在完成 Podman 安装后，为了确保 Rootless 容器能够正确挂载卷并避免权限传  播问题，必须执行以下配置。

查看根目录传播:

```sh
findmnt -o TARGET,PROPAGATION /
```

默认情况下你会看到输出结果是 `/ private`:

```sh
TARGET PROPAGATION
/ private
```

创建一个 Systemd 服务，在系统每次启动时自动设置根目录为 `shared`:

```sh
sudo vim /etc/systemd/system/make-root-shared.service
```

填入如下内容:

```ini
[Unit]
Description=Make root filesystem shared for Podman
Before=docker.service podman.service

[Service]
Type=oneshot
ExecStart=/usr/bin/mount --make-rshared /
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

加载配置:

```sh
sudo systemctl daemon-reload
```

设置开机自启并立即启动:

```sh
sudo systemctl enable --now make-root-shared.service
```

执行 `findmnt -o TARGET,PROPAGATION /` 验证根目录是否已经输出 `shared`

构建
---

### 构建 AArch64 容器

> 当你在 x86 架构的系统中希望构建运行在 aarch64 架构系统时，才需要使用指定 aarch64 目标架构。
> 默认构建会使用当前系统架构。

Podman 提供了 `--platform` 参数可以指定目标架构。

由于 x86 内核无法直接运行 arm64 指令，你需要安装 `qemu-user-static` 并将其注册到内核的 `binfmt_misc` 中，首先需要安装 QEMU 仿真器：
```sh
sudo apt install qemu-user-static binfmt-support
```

运行以下命令查看是否支持 aarch64：
```sh
ls /proc/sys/fs/binfmt_misc/qemu-aarch64
```

如果文件存在，说明内核已经知道如何处理 arm64 可执行文件了。
```sh
podman build --platform linux/arm64 -t app .
```

Podman Compose
---

安装 Podman Compose:

Debian/Ubuntu:

```sh
sudo apt install podman-compose
```

Homebrew:

```sh
brew install podman-compose
```

Podman Compose 也与 Docker Compose 完全兼容。


常见问题
---

### Podman 的网络隔离特性

Podman 与 Docker 不同，默认使用 `slirp4netns` 或 `pasta` 进行 Rootless 网络管理。在这种模式下，容器有时无法直接通过物理网卡的 IP 访问宿主机。

Podman 提供了一个特殊的域名 `host.containers.internal` 来代表宿主机。

> 在 Docker 中这个域名通常是 `host.docker.internal`。
