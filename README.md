# ragkb

一个**可插拔、可复用、可迭代**的 RAG 知识库，面向芯片原厂 SDK 技术资料（SDK 源码、开发指南
PDF/Word/Markdown、核心板原理图、客户 FAQ）的检索与问答。

> 当前状态：**M0 骨架**（项目结构 + 配置系统 + LLM/Embedding Provider 抽象 + FastAPI 健康检查
> + 测试/CI）。文档接入、向量检索、门户与权限等能力在后续里程碑中逐步加入。

## 设计原则

- **可插拔**：LLM / Embedding / OCR-VLM / 向量库 / 文档解析器均通过「接口 + 适配器」接入，配置驱动。
- **可复用**：核心能力放在 `packages/ragkb`，可拆到不同场景（客户支持、内部知识库、个人项目）复用。
- **可验证**：每个里程碑都有单元测试与 CI；功能完成并本地验证通过后才提交到 GitHub。

## 目录结构

```
ragkb/
├─ apps/
│  ├─ api/            # FastAPI 后端（入口与路由）
│  └─ cli/            # 命令行（导入/查询/评估，后续里程碑）
├─ packages/ragkb/    # 可复用核心包
│  ├─ config.py       # 配置（pydantic-settings，RAGKB_ 前缀）
│  ├─ providers/      # LLM / Embedding 适配器（OpenAI 兼容）
│  ├─ core/           # 领域模型 + RAG 编排（后续）
│  ├─ loaders/        # 文档解析器（后续）
│  ├─ chunking/       # 分块策略（后续）
│  ├─ indexing/       # 向量库与元数据仓储（后续）
│  ├─ retrieval/      # 混合检索（后续）
│  └─ eval/           # 评估（后续）
├─ tests/
├─ .github/workflows/ci.yml
└─ pyproject.toml
```

## 快速开始

要求 Python 3.11+。

```bash
# 1. 创建虚拟环境并安装（含开发依赖）
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"

# 2. 配置环境变量（复制并填写你的 API key）
cp .env.example .env

# 3. 运行测试与代码检查
pytest -q
ruff check .

# 4. 启动 API 服务
uvicorn apps.api.main:app --reload
# 访问 http://127.0.0.1:8000/health
```

## 配置

所有配置项通过环境变量（前缀 `RAGKB_`）或 `.env` 文件注入，见 `.env.example`。
LLM 与 Embedding 均采用 OpenAI 兼容协议，一套客户端即可覆盖 DeepSeek / Qwen(DashScope) /
智谱 / SiliconFlow / Moonshot / OpenAI 等后端。

## 路线图

| 里程碑 | 内容 |
| --- | --- |
| M0 | 骨架：仓库结构、配置、Provider 抽象、FastAPI 健康检查、测试/CI ✅ |
| M1 | 文档接入：PDF/Word/MD 解析 → 分块 → 入库 → CLI/API 问答（带引用） |
| M2 | Web 门户 v1：上传/管理、检索聊天、引用展示、JWT 登录 |
| M3 | 代码 + 原理图接入：tree-sitter 代码分块、原理图 OCR+VLM 描述 |
| M4 | 检索质量：BM25+向量混合、rerank、评估脚本 |
| M5 | 双门户与权限：RBAC + 按客户/型号的 collection ACL |
| M6 | 问题收集与 FAQ 闭环：Q&A 记录、反馈、相似聚类、审核沉淀 |
| M7 | 工程化：docker-compose、迁移、日志、备份、发布 v1 |

## 安全说明

API key 等敏感信息只放在本地 `.env`（已被 `.gitignore` 排除），仓库中仅保留 `.env.example`。
请勿提交真实密钥、上传的原始资料、向量库/索引数据。
