# OpenWebUI

OpenWebUI（原 Ollama WebUI）是本地运行大语言模型（LLM）最流行的方式之一。它提供了一个类似 ChatGPT 的界面，并与 Ollama 后端无缝集成，并且提供 OpenAI 后端的原生支持。

## 部署 OpenWebUI

以下是部署 OpenWebUI 的完整指南，主要分为 Docker/Podman 方式（最推荐）和 Docker Compose 方式（更易于管理）。

### 使用 Docker/Podman 进行安装

在终端（PowerShell 或 Terminal）中执行以下命令：

默认连接本地 Ollama 服务：
```sh
podman run -d \
  -p 3000:8080 \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```


指定其他服务器的 Ollama 地址：
```sh
podman run -d \
  -p 3000:8080 \
  -e OLLAMA_BASE_URL=http://example.com:11434 \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

安装支持 OpenAI 版本：
```sh
podman run -d \
  -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://example.com:8000/v1 \
  -e OPENAI_API_KEY=abc \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

安装完成后，输入地址 `http://localhost:3000` 访问界面

首次进入会提示创建管理员账号。
添加模型: 在 WebUI 中点击头像 -> 管理员面板 -> 设置 -> 模型/拉取模型。因为已经配置了 OpenAI/Ollama，这里可以直接拉取模型。
如果没有配置 OpenAI/Ollama 也可以在外部连接中管理 OpenAI/Ollama 接口。


### 使用 DockerCompose 进行安装

这种方式更容易管理配置，适合长期使用，修改配置后只需 `docker compose up -d` 即可生效。

创建项目目录：
```sh
mkdir openwebui
cd openwebui
```

创建 `docker-compose.yml` 文件
在该目录下创建一个名为 `docker-compose.yml` 的文件，内容如下：
```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    volumes:
      - openwebui:/app/backend/data
    ports:
      - "3000:8080"
    environment:
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - WEBUI_AUTH=true
      - ENABLE_OLLAMA_API=true
    extra_hosts:
      - host.docker.internal:host-gateway
    restart: unless-stopped

volumes:
  openwebui: {}
```


