# ragkb

一个**可插拔、可复用、可迭代**的 RAG 知识库，面向芯片原厂 SDK 技术资料（SDK 源码、开发指南
PDF/Word/Markdown、核心板原理图、客户 FAQ）的检索与问答。

> 当前状态：**v1.0.0 已发布**（M0–M7 全部完成：文档/代码/原理图接入、Web 门户、混合检索、
> 双门户权限、FAQ 闭环、Docker 化）。

## 设计原则

- **可插拔**：LLM / Embedding / OCR-VLM / 向量库 / 文档解析器均通过「接口 + 适配器」接入，配置驱动。
- **可复用**：核心能力放在 `packages/ragkb`，可拆到不同场景（客户支持、内部知识库、个人项目）复用。
- **可验证**：每个里程碑都有单元测试与 CI；功能完成并本地验证通过后才提交到 GitHub。

## 目录结构

```
ragkb/
├─ apps/
│  ├─ api/            # FastAPI 后端（/health、/auth、/ingest、/ask、/documents、/users、/qa）
│  └─ cli/            # 命令行（ingest / ask）
├─ packages/ragkb/    # 可复用核心包
│  ├─ config.py       # 配置（pydantic-settings，RAGKB_ 前缀）
│  ├─ auth.py         # 密码散列 + JWT 令牌
│  ├─ providers/      # LLM / Embedding 适配器（OpenAI 兼容 + 本地 BGE + fake 离线）
│  ├─ core/           # 领域模型、摄入/问答管线、客户-型号 ACL
│  ├─ loaders/        # PDF / Word / Markdown / 源码 / 原理图(VLM) 解析器
│  ├─ chunking/       # 分块策略（文本 + 源码结构感知）
│  ├─ indexing/       # SQLite 向量库 + 用户存储 + Q&A 记录（可插拔 VectorStore 接口）
│  ├─ retrieval/      # 向量 + BM25 混合检索（RRF）、可插拔 rerank
│  ├─ web/            # 内置单页门户（登录 / 上传 / 问答）
│  └─ eval/           # 检索评估（Hit@k / MRR）
├─ tests/
├─ .github/workflows/ci.yml
└─ pyproject.toml
```

## 快速开始

> 逐项测试清单与记录见 [docs/testing.md](docs/testing.md)。

要求 Python 3.11+。

```bash
# 1. 创建虚拟环境并安装（含开发依赖）
python -m venv .venv
# Windows（若 activate 报“无法加载模块 .venv”，改用 .\.venv\Scripts\Activate.ps1，
# 或干脆不激活、直接用 .venv\Scripts\python 前缀执行）:
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

# 5. 命令行摄入文档并提问（需要真实 API key，或用 fake 离线演示）
python -m apps.cli.main ingest ./docs/
python -m apps.cli.main ask "如何配置 GPIO 引脚？"
python -m apps.cli.main list                              # 列出已入库来源
python -m apps.cli.main delete ./docs/wrong.pdf           # 删除某来源（撤回错误文件）
python -m apps.cli.main eval examples/eval_example.json   # 检索质量评估（Hit@k / MRR）
python -m apps.cli.main backup ./backups/                  # 备份 SQLite 库

# 6. 打开浏览器访问 http://127.0.0.1:8000/ （内置 Web 门户，默认账号 admin / admin123）

# 7. 或通过 API：先登录拿 token，再上传文档并提问
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r .token)
curl -F "file=@docs/guide.md" http://127.0.0.1:8000/ingest \
  -H "Authorization: Bearer $TOKEN"
curl -X POST http://127.0.0.1:8000/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "如何配置 GPIO 引脚？"}'
```

> 离线演示（无 API key）：在 `.env` 中把 `RAGKB_LLM_PROVIDER` 与
> `RAGKB_EMBEDDING_PROVIDER` 设为 `fake`，即可用确定性的内置实现跑通摄入与检索流程。

## 配置

所有配置项通过环境变量（前缀 `RAGKB_`）或 `.env` 文件注入，见 `.env.example`。
LLM 与 Embedding 默认采用 OpenAI 兼容协议，一套客户端即可覆盖 DeepSeek / Qwen(DashScope) /
智谱 / SiliconFlow / Moonshot / OpenAI 等后端；Embedding 也可设为 `local`，用本地
sentence-transformers（BGE）离线向量化，数据不出内网（`pip install -e ".[local]"`）。
VLM（原理图描述）同样走 OpenAI 兼容多模态协议（如 Qwen-VL / GPT-4o）。

## 权限与双门户

- 角色：`admin`（全量）、`support`（内部支持，全量检索）、`customer`（客户自助，仅见被授权资料）。
- 资料在摄入时打上 `customer`/`model` 标签；客户账号通过 `customers`/`models` 白名单限定可见范围。
- 内部门户（上传/管理资料、用户管理）仅 `admin`/`support` 可用；客户门户只做问答（自动按 ACL 隔离）。

```bash
# 管理员创建一个客户账号（仅能看 acme 客户的 x1 型号资料）
curl -X POST http://127.0.0.1:8000/users \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"username":"acme","password":"acme-pass","role":"customer","customers":["acme"],"models":["x1"]}'

# 摄入时打标签
curl -F "file=@sdk.zip" -F "customer=acme" -F "model=x1" \
  -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/ingest
```

## Docker 部署

```bash
docker compose up --build
# 访问 http://localhost:8000/ （默认账号 admin / admin123）
```

密钥等通过环境变量或 `.env` 注入（见 `docker-compose.yml` 与 `.env.example`）。默认使用
`fake` 离线 provider 便于快速启动；生产时把 `RAGKB_LLM_PROVIDER` / `RAGKB_EMBEDDING_PROVIDER`
改为 `openai-compatible` 并填入 key。SQLite 数据保存在 `ragkb-data` 卷，可用
`docker compose run --rm ragkb python -m apps.cli.main backup /data/backup` 备份。

## 路线图

| 里程碑 | 内容 |
| --- | --- |
| M0 | 骨架：仓库结构、配置、Provider 抽象、FastAPI 健康检查、测试/CI ✅ |
| M1 | 文档接入：PDF/Word/MD 解析 → 分块 → 入库 → CLI/API 问答（带引用）✅ |
| M2 | Web 门户 v1：上传/管理、检索聊天、引用展示、JWT 登录 ✅ |
| M3 | 代码 + 原理图接入：代码结构感知分块、原理图 VLM 描述 ✅ |
| M4 | 检索质量：BM25+向量混合、rerank、评估脚本 ✅ |
| M5 | 双门户与权限：RBAC + 按客户/型号的 collection ACL ✅ |
| M6 | 问题收集与 FAQ 闭环：Q&A 记录、反馈、相似聚类、审核沉淀 ✅ |
| M7 | 工程化：docker-compose、日志、备份、发布 v1 ✅ |

## 安全说明

API key 等敏感信息只放在本地 `.env`（已被 `.gitignore` 排除），仓库中仅保留 `.env.example`。
请勿提交真实密钥、上传的原始资料、向量库/索引数据。部署前请务必修改 `RAGKB_JWT_SECRET` 与
默认管理员密码 `RAGKB_DEFAULT_ADMIN_PASSWORD`。
