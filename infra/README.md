# LLM Infra Stack

LLM 生态的基础组件托管方案。通过 Docker Compose 的 include 模式，将 Milvus、Elasticsearch、NebulaGraph 及可视化工具实现为一个可插拔的集成环境，支持一键拉起 RAG 所需的核心基础设施。

## 架构设计

本部署架构采用 “1+N” 模式：
- 1 个主入口 (`docker-compose.yml`)：负责定义全局共享网络 `db-net` 和服务编排逻辑。
- N 个功能模块 (`*_include.yml`)：每个模块独立管理其核心服务及其依赖（如 Etcd, MinIO 等），实现配置解耦。

## 快速开始

### 环境准备
在启动之前，请确保宿主机满足以下要求：

- 操作系统: Linux (推荐 Ubuntu 22.04+)
- 内核参数:
    Elasticsearch 需要调高 `mmap` 计数。请执行：
    ```bash
    sudo sysctl -w vm.max_map_count=262144
    ```
- 配置目录: 脚本会自动在当前目录下创建 `./storage` 文件夹用于持久化。

### 启动命令示例

在 `infra/` 目录下，根据业务需求通过 `--profile` 参数灵活组合需要启动的堆栈：

| 场景 | 启动命令 |
| :--- | :--- |
| 全量启动 | `docker compose --profile es --profile milvus --profile nebula up -d` |
| 仅搜索与图谱 (ES + Nebula) | `docker compose --profile es --profile nebula up -d` |
| 停止所有服务 | `docker compose --profile es --profile milvus --profile nebula down` |

## 运维指南

### 常用管理地址汇总
| 服务 | 访问地址 | 默认凭据 |
| :--- | :--- | :--- |
| Kibana (Elasticsearch) | `http://localhost:15601` | 无 |
| Attu (Milvus) | `http://localhost:3000` | 无 |
| Nebula Studio | `http://localhost:7001` | root / nebula |

### 状态查看
查看当前运行的服务及其资源占用情况：
```bash
docker stats
```

### 日志调试
如果某个模块启动失败，可以针对性查看该 profile 的日志。

例如，查看 milvus 的实时日志：
```bash
docker compose --profile milvus logs -f standalone
```

### 数据清理
若需彻底重置环境：
```bash
docker compose --profile es --profile milvus --profile nebula down -v
rm -rf ./storage ./volumes
```

> 注意：这会删除所有数据库内容。

## 注意事项
1. 资源预留: 所有组件的资源配额均针对 16G 内存的宿主机进行配置。
2. 网络隔离: 所有服务均加入名为 `shared_database_network` 的网络，容器间可通过 `service_name` 直接通信。
3. 安全性: 当前配置为开发/测试优化，所有组件均禁用了密码或使用默认密码。

## 目录结构
```text
infra/
├── docker-compose.yml         # 主入口，定义网络与全局编排
├── nebula_include.yml         # NebulaGraph 服务组件
├── milvus_include.yml         # Milvus 服务组件
├── elasticsearch_include.yml  # Elasticsearch 服务组件
├── storage/                   # Nebula 持久化数据（运行时生成）
└── volumes/                   # Milvus 相关持久化数据（运行时生成）
```
