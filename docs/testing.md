# ragkb 测试手册

> 本文件是**持续更新的测试记录**：按下面步骤一项一项测，每一步把「实际结果」填进去；
> 遇到报错就把**命令 + 完整报错**贴到文末「问题记录」表格里。
>
> 当前版本：v1.0.0　｜　最后更新：2026-08-26

## 0. 前置约定（先读）

- 所有命令都在 `D:\Code\AI\RAG` 目录下执行。
- **不要用 `.venv\Scripts\activate`**（PowerShell 下会报「无法加载模块 .venv」）。
  统一直接用虚拟环境里的解释器：`.venv\Scripts\python`。
- PowerShell 里 `curl` 是 `Invoke-WebRequest` 的别名，语法不一样；本手册所有 curl 一律写
  **`curl.exe`**（Windows 10 自带真正的 curl）。
- 离线测试用 fake provider，**不需要任何 API key**；要真实效果再看「第 7 节」。
- 已知无害现象：`GET /favicon.ico -> 404` 正常；地址栏里误输入文字会看到
  `GET /%2A%2A...` 的 404，忽略即可。

---

## 1. 自动化测试 ✅

```powershell
.venv\Scripts\python -m pytest -q   # 预期：78 passed
.venv\Scripts\ruff check .          # 预期：All checks passed!
```

- [x] 2026-08-26 结果：`78 passed in 5.81s`、`All checks passed!` ✅

---

## 2. 启动服务（离线 fake 模式）

```powershell
$env:RAGKB_LLM_PROVIDER = "fake"
$env:RAGKB_EMBEDDING_PROVIDER = "fake"
$env:RAGKB_VLM_PROVIDER = "fake"      # 可选：想测「原理图 PDF 识别」才需要
.venv\Scripts\python -m uvicorn apps.api.main:app --reload
```

预期日志：`Uvicorn running on http://127.0.0.1:8000`。

- [x] 2026-08-26 结果：启动成功，浏览器能打开首页 ✅

> 注意：上面 `$env:...` 只对**当前这个 PowerShell 窗口**生效。关掉窗口就失效。
> 后面第 7 节要填真实 key 时，必须先把这些 fake 变量清掉（或新开一个窗口）。

---

## 3. Web 门户功能测试（浏览器）

打开 **http://127.0.0.1:8000/**，默认账号 `admin` / `admin123`。

| 步骤 | 操作 | 预期 | 结果 |
|---|---|---|---|
| 3.1 登录 | 用 admin/admin123 登录 | 进入主界面 | [x] ✅ |
| 3.2 上传文档 | 上传一个 .md / .pdf / .docx | 文档列表出现该项 | [ ] |
| 3.3 问答 | 问一句文档里有的话 | 返回答案 + `[n] 来源/页码` 引用 | [ ] |
| 3.4 文档管理 | 在列表里删除某文档 | 删除后列表消失该项 | [ ] |

> 3.3 在 fake 模式下答案是固定的 `This is a fake answer.`，但**引用来源**是真实检索出来的，
> 能验证「文档确实被切块/建索引/检索到」。

---

## 4. API 功能测试（curl.exe）

> 下面用到的 `$token` 变量在同一个窗口里定义一次即可，之后一直复用。

### 4.1 登录拿 token

```powershell
$resp = curl.exe -s -X POST http://127.0.0.1:8000/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'
$resp
$token = ($resp | ConvertFrom-Json).token
```

预期：返回一段 JSON，里面有 `token`。

### 4.2 上传文档并打客户标签（multipart）

```powershell
curl.exe -s -X POST http://127.0.0.1:8000/ingest -H "Authorization: Bearer $token" -F "file=@D:\Code\AI\RAG\examples\eval_example.json" -F "customer=acme" -F "model=x1"
```

预期：返回类似 `{"chunks": N, ...}`，N > 0。

### 4.3 问答（带引用）

```powershell
curl.exe -s -X POST http://127.0.0.1:8000/ask -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d '{"question":"GPIO 怎么初始化？"}'
```

预期：返回 `{"answer": "...", "citations": [{"source": "...", "page": null, "snippet": "..."}]}`。

### 4.4 双门户 ACL（创建客户账号 → 验证隔离）

```powershell
# 管理员创建客户账号：只允许看 acme 客户、x1 型号的资料
curl.exe -s -X POST http://127.0.0.1:8000/users -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d '{"username":"acme","password":"acme-pass","role":"customer","customers":["acme"],"models":["x1"]}'

# 用客户账号登录
$resp2 = curl.exe -s -X POST http://127.0.0.1:8000/auth/login -H "Content-Type: application/json" -d '{"username":"acme","password":"acme-pass"}'
$acmeToken = ($resp2 | ConvertFrom-Json).token

# 客户访问用户管理接口：应被拒绝
curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:8000/users -H "Authorization: Bearer $acmeToken"
```

预期：最后一行输出 `403`（客户无权管理用户）。

> 更完整的隔离验证：上传一份 `customer=acme` 和一份 `customer=other` 的文档，用 `$acmeToken`
> 调 `/ask`，引用里只应出现 acme 那份。

### 4.5 FAQ 闭环（提问 → 反馈 → 沉淀 → 再次命中）

```powershell
# 1. 先问一次，会产生一条 Q&A 记录
curl.exe -s -X POST http://127.0.0.1:8000/ask -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d '{"question":"GPIO 怎么初始化？"}'

# 2. 查看最近 Q&A，记下 id
curl.exe -s http://127.0.0.1:8000/qa/recent -H "Authorization: Bearer $token"

# 3. 反馈（1=有用 / 0=没用）
curl.exe -s -X POST http://127.0.0.1:8000/qa/1/feedback -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d '{"feedback":1}'

# 4. 沉淀为 FAQ（会把该问答重新写入知识库，以后能被检索到）
curl.exe -s -X POST http://127.0.0.1:8000/qa/1/promote -H "Authorization: Bearer $token"
```

> 步骤 3、4 里的 `/qa/1/...` 里的 `1` 换成第 2 步看到的真实 id。
> promote 后再调 `/ask`，引用里应多出一个 `source` 形如 `faq:1` 的来源。

### 4.6 相似问题

```powershell
curl.exe -s "http://127.0.0.1:8000/qa/similar?question=GPIO&k=5" -H "Authorization: Bearer $token"
```

预期：返回 `{"similar": [{"id":1,"question":"...","score":0.xx}, ...]}`。

---

## 5. 命令行测试（CLI）

> CLI 也走配置，离线时先设 fake 环境变量（同第 2 节）。

```powershell
# 摄入一个目录（含子目录里的 .md/.pdf/.docx/.c/.h 等）
.venv\Scripts\python -m apps.cli.main ingest examples
# 预期：Ingested N chunks.

# 问答
.venv\Scripts\python -m apps.cli.main ask "GPIO 怎么初始化？"
# 预期：打印答案 + [1] source p.page 引用

# 检索质量评估（Hit@k / MRR）
.venv\Scripts\python -m apps.cli.main eval examples\eval_example.json
# 预期：num_questions / hit@4 / mrr 三行

# 备份 SQLite 库
.venv\Scripts\python -m apps.cli.main backup .\backups\
# 预期：Backed up data\ragkb.sqlite -> ...\ragkb.sqlite.backup
```

---

## 6. Docker 部署测试（可选）

```powershell
docker compose up --build
# 打开 http://localhost:8000/（账号 admin/admin123）
```

预期：镜像构建成功、容器起来、能登录。

> 若 8000 端口已被第 2 节的本地 uvicorn 占用，先 `Ctrl+C` 停掉本地服务再跑。
> 默认也是 fake provider，离线可跑通；数据存在 `ragkb-data` 卷里。

---

## 7. 填入真实 API key（真实效果测试）

1. 复制 `.env.example` → `.env`，把下面三段填成自己的 key：

```ini
RAGKB_LLM_BASE_URL=https://api.deepseek.com/v1
RAGKB_LLM_API_KEY=sk-你的LLM-key
RAGKB_LLM_MODEL=deepseek-chat

RAGKB_EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
RAGKB_EMBEDDING_API_KEY=sk-你的Embedding-key
RAGKB_EMBEDDING_MODEL=BAAI/bge-m3

RAGKB_VLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
RAGKB_VLM_API_KEY=sk-你的VLM-key
RAGKB_VLM_MODEL=qwen-vl-max
RAGKB_VLM_PROVIDER=openai-compatible
```

2. **清掉 fake 环境变量**（否则它会覆盖 `.env`），最省事是**新开一个 PowerShell 窗口**；
   或手动清除：

```powershell
Remove-Item Env:RAGKB_LLM_PROVIDER -ErrorAction SilentlyContinue
Remove-Item Env:RAGKB_EMBEDDING_PROVIDER -ErrorAction SilentlyContinue
Remove-Item Env:RAGKB_VLM_PROVIDER -ErrorAction SilentlyContinue
```

3. 重启服务：

```powershell
.venv\Scripts\python -m uvicorn apps.api.main:app --reload
```

4. 重新走一遍第 3、4 节的问答，此时答案应为真实模型生成、引用为真实向量检索结果。

> 注意：`RAGKB_LLM_PROVIDER` / `RAGKB_EMBEDDING_PROVIDER` 在 `.env` 里默认就是
> `openai-compatible`，只要填了 key 即可；不填 key 启动会在调用时返回 503（属预期，缺 key 保护）。

---

## 8. 问题记录（发现的问题往这里补）

| 日期 | 步骤 | 现象/报错（命令 + 完整输出） | 状态 |
|---|---|---|---|
| 2026-08-26 | 0 | `.venv\Scripts\activate` 报「无法加载模块 .venv」 | 已解决：改用 `.venv\Scripts\python` 直接执行 |
|  |  |  |  |
