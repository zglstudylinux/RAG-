# ragkb 测试手册

> 本文件是**持续更新的测试记录**：按下面步骤一项一项测，每一步把「实际结果」填进去；
> 遇到报错就把**命令 + 完整报错**贴到文末「问题记录」表格里。
>
> 当前版本：v1.0.0　｜　最后更新：2026-08-26

## 0. 前置约定（先读）

- 所有命令都在 `D:\Code\AI\RAG` 目录下执行。
- **不要用 `.venv\Scripts\activate`**（PowerShell 下会报「无法加载模块 .venv」）。
  统一直接用虚拟环境里的解释器：`.venv\Scripts\python`。
- PowerShell 里 `curl` 是 `Invoke-WebRequest` 的别名，语法不一样。
  **JSON 请求用 `Invoke-RestMethod`**（见第 4 节）；只有文件上传/看状态码用 `curl.exe`
  （Windows 10 自带真正的 curl）。
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

## 4. API 功能测试（PowerShell：Invoke-RestMethod）

> ⚠️ 不要用 `curl.exe -d` 传 JSON——Windows PowerShell 会把 JSON 里的双引号吞掉，导致
> `json_invalid`。JSON 请求统一用 PowerShell 原生的 `Invoke-RestMethod`（可靠、无转义坑）；
> 只有**文件上传**（multipart）和**只看状态码**两处用 `curl.exe`（无嵌套引号，不受影响）。
>
> ⚠️ 中文请求体：PowerShell 5.1 的 `Invoke-RestMethod -Body` 传**字符串**时会把中文写成 `?`。
> 凡 body 里含中文（`/ask` 的 question），必须先把 JSON 转成 **UTF-8 字节**再传（见 4.3）。
> 纯 ASCII 的 body（登录/建用户/反馈）不受影响，可继续用字符串。
>
> ⚠️ 控制台显示中文乱码是 PowerShell 5.1 的**显示**问题，**数据库里存的是正确的中文**；
> 要确认中文内容，用浏览器页面（能正常显示）或查 `data/ragkb.sqlite` 对照即可。
>
> 下面用到的 `$token` 变量在同一个窗口里定义一次即可，之后一直复用。

> ✅ 2026-08-26 已验证：4.1 token、4.2 上传(7 chunks)、4.4 建账号+403 隔离、4.5 recent/feedback/promote、
> 4.6 similar 全部正常。4.3/4.5 的 `/ask` 中文 question 之前被写成 `?`，已按上面 UTF-8 字节方式修正，
> 重跑 4.3 即可看到库里存进正确中文。

### 4.1 登录拿 token

```powershell
$resp = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/auth/login -ContentType "application/json" -Body '{"username":"admin","password":"admin123"}'
$resp
$token = $resp.token
```

预期：`$resp` 里能看到 `token` 字段；`$token` 有值。

### 4.2 上传文档并打客户标签（multipart，用 curl.exe）

```powershell
curl.exe -s -X POST http://127.0.0.1:8000/ingest -H "Authorization: Bearer $token" -F "file=@D:\Code\AI\RAG\README.md" -F "customer=acme" -F "model=x1"
```

预期：返回 `{"chunks": N, ...}`，N > 0。

### 4.3 问答（带引用，中文 question 需转 UTF-8 字节）

```powershell
$q = '{"question":"如何配置 GPIO 引脚？"}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/ask -Headers @{Authorization="Bearer $token"} -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($q))
```

预期：返回对象含 `answer` 和 `citations`（每个 citation 有 `source`）。

### 4.4 双门户 ACL（创建客户账号 → 验证隔离）

```powershell
# 管理员创建客户账号：只允许看 acme 客户、x1 型号的资料
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/users -Headers @{Authorization="Bearer $token"} -ContentType "application/json" -Body '{"username":"acme","password":"acme-pass","role":"customer","customers":["acme"],"models":["x1"]}'

# 用客户账号登录
$resp2 = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/auth/login -ContentType "application/json" -Body '{"username":"acme","password":"acme-pass"}'
$acmeToken = $resp2.token

# 客户访问用户管理接口：应被拒绝（用 curl.exe 只看状态码）
curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:8000/users -H "Authorization: Bearer $acmeToken"
```

预期：最后一行输出 `403`（客户无权管理用户）。

> 更完整的隔离验证：上传一份 `customer=acme` 和一份 `customer=other` 的文档，用 `$acmeToken`
> 调 `/ask`，引用里只应出现 acme 那份。

### 4.5 FAQ 闭环（提问 → 反馈 → 沉淀 → 再次命中）

```powershell
# 1. 先问一次，会产生一条 Q&A 记录（中文 question 转 UTF-8 字节）
$q = '{"question":"如何配置 GPIO 引脚？"}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/ask -Headers @{Authorization="Bearer $token"} -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($q)) | Out-Null

# 2. 查看最近 Q&A，记下 id
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/qa/recent -Headers @{Authorization="Bearer $token"}

# 3. 反馈（1=有用 / 0=没用；把 /qa/1/ 里的 1 换成第 2 步的真实 id）
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/qa/1/feedback -Headers @{Authorization="Bearer $token"} -ContentType "application/json" -Body '{"feedback":1}'

# 4. 沉淀为 FAQ（把该问答重新写入知识库，以后能被检索到）
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/qa/1/promote -Headers @{Authorization="Bearer $token"}
```

> promote 后再调 `/ask`，引用里应多出一个 `source` 形如 `faq:1` 的来源。

### 4.6 相似问题

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/qa/similar?question=GPIO&k=5" -Headers @{Authorization="Bearer $token"}
```

预期：返回对象含 `similar` 数组（`id`、`question`、`score`）。

---

## 5. 命令行测试（CLI）

> ⚠️ CLI 和 API 服务一样读配置：**离线测试（无 API key）时必须先设 fake 环境变量**，
> 否则报 `ConfigurationError: Embedding API key is not configured`。每个新窗口都要设一次。

```powershell
# 0. 先设 fake provider（离线模式）
$env:RAGKB_LLM_PROVIDER = "fake"
$env:RAGKB_EMBEDDING_PROVIDER = "fake"
```

```powershell
# 摄入单个文件（README.md → 7 chunks）或目录（docs → N chunks，随文件大小变化）
.venv\Scripts\python -m apps.cli.main ingest README.md
.venv\Scripts\python -m apps.cli.main ingest docs

# 问答（fake 模式答案固定英文，引用来源是真实检索）
.venv\Scripts\python -m apps.cli.main ask "GPIO 怎么初始化？"

# 检索质量评估（Hit@k / MRR）
.venv\Scripts\python -m apps.cli.main eval examples\eval_example.json

# 备份 SQLite 库（这一步不需要 fake 环境变量，只复制文件）
.venv\Scripts\python -m apps.cli.main backup .\backups\
```

> 说明：
> - `ingest examples` 会得到 `Ingested 0 chunks.`，因为 `examples/` 里只有 `eval_example.json`
>   （评估模板，不是可摄入的文档类型）。要摄入文档请用 `README.md` / `docs` / 你自己的资料。
> - `eval examples\eval_example.json` 打印 `num_questions / hit@4 / mrr` 三行；它的
>   `relevant_sources` 是 `gpio`/`uart`/`i2c`（模板占位），库里没有这些来源时 `hit@4`、`mrr`
>   都是 `0.000`，属预期。换你自己的真实「问题 + 来源」即可得到有效指标。
> - CLI 输出的中文在控制台可能显示乱码，是 PowerShell 控制台编码问题，不影响功能。
> - 填了真实 API key 后（第 7 节），**不要再设 `fake`**，直接跑 CLI 即走真实模型。

> ✅ 2026-08-26 已验证：`ingest README.md`=7 chunks、`ingest docs`=13 chunks；`ask` 返回 4 条引用
> 且第一条是 `faq:1`（第 4.5 节沉淀的 FAQ 被检索命中，闭环打通）；`eval` 正常打印三行
> （hit@4/mrr=0.000 因占位符来源）；`backup` 成功。首行 `Building prefix dict...` 是 jieba
> 首次加载词典，正常。

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
| 2026-08-26 | 4.1 | `curl.exe -d '{"username":...}'` 报 `json_invalid`（JSON 双引号被 PowerShell 吞掉） | 已解决：JSON 请求改用 `Invoke-RestMethod` |
| 2026-08-26 | 4.3/4.5 | `Invoke-RestMethod -Body` 传中文 question 被存成 `???? GPIO ???` | 已解决：JSON 先 `[System.Text.Encoding]::UTF8.GetBytes()` 转字节再传 |
| 2026-08-26 | 5 | CLI 报 `ConfigurationError: Embedding API key is not configured` | 已解决：跑 CLI 前先 `$env:RAGKB_LLM_PROVIDER="fake"`、`$env:RAGKB_EMBEDDING_PROVIDER="fake"`（backup 除外） |
|  |  |  |  |
