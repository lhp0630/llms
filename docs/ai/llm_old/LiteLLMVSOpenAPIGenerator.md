- [概述](#概述)
- [什么是 LiteLLM](#什么是litellm)
- [什么是 OpenAPI Generator](#什么是openapigenerator)
- [LiteLLM 快速上手](#litellm快速上手)
- [OpenAPI Generator 快速上手](#openapigenerator快速上手)

## 概述

在 AI 开发的生态中，如何让非 OpenAI 的模型（如 Claude, Gemini, Llama）完美适配那些只认 OpenAI 接口的现有软件？

目前主流有两种完全不同的进化路径：一种是 OpenAPI Generator，另一种是 LiteLLM Proxy。本文将重点介绍 LiteLLM Proxy，并对比这两者的优劣。

## 什么是 LiteLLM

LiteLLM Proxy 是一个开箱即用的服务器，支持 Binary 或 Docker 部署。它在前端暴露完全兼容 OpenAI 的 API 接口，而在后端自动将请求转换为 100 多种不同 LLM 供应商的原生协议。

```
                +-------------+
User Request -> |   LiteLLM   |
                +------+------+ 
                       |
      +----------------+----------------+
      |                                 |
+------------+                    +------------+
| OpenAI API |                    | Local vLLM |
+------------+                    +------------+
```

### LiteLLM 的优势

- 零代码适配：你不需要写代码，只需要一个 `config.yaml` 配置文件。
- 身份验证与安全：内置 API Key 管理，你可以为不同的团队生成不同的 Key，并设置模型权限。
- 负载均衡与故障转移：如果 OpenAI 挂了，Proxy 会在毫秒级自动把请求重定向到 Anthropic 或 Azure。
- 看板与监控：自带 Web UI，可以实时查看 Token 消耗、费用支出和响应延迟。

## 什么是 OpenAPI Generator

OpenAPI Generator 是基于 OpenAI 官方的 Swagger 定义来生成一个 FastAPI/Flask 服务骨架，并支持其他语言如 Java/C#/Go 等。

OpenAPI Generator 生成代码后，仍需手动编写每个 Endpoint 的内部逻辑（即：如何把接收到的 OpenAI 格式参数手动映射到 Claude 的 SDK 上）。这涉及到大量的胶水代码开发，这非常适合需要高度定制且兼容 OpenAI 规范的 API 接口开发需求。

## LiteLLM 快速上手

LiteLLM `config.yaml` 配置示例:

```yaml
model_list:
  - model_name: fake-openai-endpoint # 对外暴露的名字
    litellm_params:
      model: openai/fake-model # 实际调用的后端
      api_key: fake-key
      api_base: https://exampleopenaiendpoint-production.up.railway.app/

# 模型路由配置
# 简单问题 -> 小模型
# 复杂问题 -> 大模型
router_settings:
  routing_strategy: simple-shuffle
  num_retries: 3
  timeout: 30

general_settings:
  master_key: sk-1234

litellm_settings:
  success_callback: ["prometheus"]
```

`prometheus.yml` 配置:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'litellm'
    static_configs:
      - targets: ['litellm:4000']  # Assuming Litellm exposes metrics at port 4000
```

### Docker 方式部署 LiteLLM

```sh
podman pull ghcr.io/berriai/litellm:main
docker run -d -p 4000:4000 -v $(pwd)/config.yaml:/app/config.yaml ghcr.io/berriai/litellm:main --config /app/config.yaml
```

### Docker Compose 方式部署 LiteLLM

```yaml
version: "3"

services:
  litellm:
    image: ghcr.io/berriai/litellm:main
    ports:
      - "4000:4000"
    volumes:
      - ./config.yaml:/app/config.yaml
    command: ["--config", "/app/config.yaml"]
```

完整 Docker Compose 配置示例:
```yaml
version: "3.9"

services:
  litellm:
    image: ghcr.io/berriai/litellm:main
    container_name: litellm
    restart: always
    command:
      - "--config"
      - "/app/config.yaml"
      - "--port"
      - "4000"
    ports:
      - "4000:4000"
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./logs:/app/logs
    env_file:
      - .env
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    container_name: litellm-db
    restart: always
    environment:
      POSTGRES_DB: litellm
      POSTGRES_USER: litellm
      POSTGRES_PASSWORD: litellm_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  prometheus:
    image: prom/prometheus
    container_name: litellm-prometheus
    restart: always
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

volumes:
  postgres_data: {}
```

## OpenAPI Generator 快速上手

安装 OpenAPI Generator:
```sh
npm install -g @openapitools/openapi-generator-cli
```

下载 OpenAI Swagger 文档 [openapi.with-code-samples.yml](https://app.stainless.com/api/spec/documented/openai/openapi.documented.yml):
```sh
curl -fsSLo openapi.with-code-samples.yml https://app.stainless.com/api/spec/documented/openai/openapi.documented.yml
```

生成代码:
```sh
openapi-generator-cli generate -i openapi.with-code-samples.yml -g python-fastapi -p packageName=openai_server -o ./openai_prosvc
```
