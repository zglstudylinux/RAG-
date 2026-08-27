# ragkb 测试手册

> 本文件是**持续更新的测试记录**：按下面步骤一项一项测，每一步把「实际结果」填进去；
> 遇到报错就把**命令 + 完整报错**贴到文末「问题记录」表格里。
>
> 当前版本：v1.1.0　｜　最后更新：2026-08-26

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
.venv\Scripts\python -m pytest -q   # 预期：110 passed
.venv\Scripts\ruff check .          # 预期：All checks passed!
```

- [x] 2026-08-26 结果：`101 passed in 7.10s`、`All checks passed!` ✅
- [x] 2026-08-26 结果：`105 passed in 8.88s`、`All checks passed!` ✅（新增：分类列过滤、文件夹分组/整组删除）
- [x] 2026-08-26 结果：`108 passed in 9.21s`、`All checks passed!` ✅（新增：FAQ 沉淀存储/检索/API、FAQ 优先命中）
- [x] 2026-08-26 结果：`110 passed in 10.04s`、`All checks passed!` ✅（新增：FAQ 旧引用编号剥离、FAQ 命中引用清洁）

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

### 4.7 分类管理（多芯片 / 多业务）

```powershell
# 建业务域（⚠️ 含中文的 name 也要走 UTF-8 字节，同 4.3）
$body = [System.Text.Encoding]::UTF8.GetBytes('{"name":"芯片SDK"}')
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/categories -Headers @{Authorization="Bearer $token"} -ContentType "application/json; charset=utf-8" -Body $body

# 建分类（挂到某业务域下）
$body = [System.Text.Encoding]::UTF8.GetBytes('{"name":"AB5766C","parent":"芯片SDK"}')
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/categories -Headers @{Authorization="Bearer $token"} -ContentType "application/json; charset=utf-8" -Body $body

# 列出分类（含每类的块数）
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/categories -Headers @{Authorization="Bearer $token"}

# 上传资料并打分类标签（.zip 会自动解压）
curl.exe -s -X POST http://127.0.0.1:8000/ingest -H "Authorization: Bearer $token" -F "file=@sdk.zip" -F "category=AB5766C"

# 按分类过滤资料列表
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/documents?category=AB5766C" -Headers @{Authorization="Bearer $token"}

# 重命名分类（会同步改其下资料标签） / 删除分类（级联删除其下资料）
Invoke-RestMethod -Method Patch -Uri http://127.0.0.1:8000/categories/AB5766C -Headers @{Authorization="Bearer $token"} -ContentType "application/json" -Body '{"new_name":"AB5766D"}'
Invoke-RestMethod -Method Delete -Uri http://127.0.0.1:8000/categories/AB5766D -Headers @{Authorization="Bearer $token"}
```

> 一次性预置默认分类（芯片SDK → AB5766C/AB573X/BT897X/BT895X）并把现有 5766 资料回填到
> AB5766C（幂等，可重复执行）：`.venv\Scripts\python scripts\seed_categories.py`

> 浏览器端：「分类管理」标签页可建/重命名/删分类；「资料管理」上传时选分类、按分类分组查看/删除；
> 「问答」里可限定某个分类提问。

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

> ⚠️ 2026-08-26 本机**未安装 Docker**（`docker` 命令不存在、无 Docker Desktop 服务），此节暂未测。
> 装好 Docker Desktop 后跑下面命令即可；**此节可选**——不装 Docker 也能用第 2 节的本地方式跑完整功能。

> **本机安装 Docker 的步骤**（Windows 11 家庭版无 Hyper-V，走 WSL2 后端；需管理员 + 重启）：
> 1. 管理员 PowerShell 运行 `wsl --install` → **重启电脑**（重启后按提示设 Ubuntu 用户名/密码）。
> 2. 下载安装 Docker Desktop：https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
>    （约 540MB，双击一路默认，家庭版自动用 WSL2）。
> 3. 启动 Docker Desktop，等鲸鱼图标提示 `Docker Desktop is running` 后验证 `docker --version`。

```powershell
docker compose up --build
# 打开 http://localhost:8000/（账号 admin/admin123）
```

预期：镜像构建成功、容器起来、能登录。

> 若 8000 端口已被第 2 节的本地 uvicorn 占用，先 `Ctrl+C` 停掉本地服务再跑。
> 默认也是 fake provider，离线可跑通；数据存在 `ragkb-data` 卷里。

### 6.1 在 VMware Ubuntu 24.04 里测 Docker（推荐）

Linux 原生跑 Docker，**不用 WSL / 管理员 / 重启 Windows**，比在 Windows 上装 Docker Desktop 省事得多。

```bash
# 1. 安装 Docker Engine + compose 插件（官方一键脚本）
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker                 # 立即生效，或重新登录

# 2. 验证
docker --version
docker compose version

# 3. 拉项目代码（没有 git 先 sudo apt install -y git）
cd ~
git clone https://github.com/zglstudylinux/RAG-.git
cd RAG-

# 4. 构建并启动（首次构建需联网下载 python:3.11-slim 与 pip 依赖，几分钟）
docker compose up --build
```

- **从 Windows 访问**：在 VM 里 `ip addr` 查 IP（eth0/ens33 的 inet，形如 192.168.x.x），
  然后 Windows 浏览器打开 `http://<VM-IP>:8000/`（账号 admin / admin123）。
- **网络要求**：首次构建要联网拉镜像和 pip 包；VMware NAT 通常可直接上外网。若 VM 不能直连
  外网（需走 Windows 上的代理 127.0.0.1:7897），则把代理指向宿主机 IP 并允许局域网连接，
  再 `export HTTP_PROXY=http://<宿主机IP>:7897`、`export HTTPS_PROXY=...`。
- ✅ 已本地验证：Dockerfile 的启动命令（裸 `uvicorn apps.api.main:app`）可正常启动，`/health`
  返回 `version 1.0.0`。

---

## 7. 真实模型测试（LLM/VLM 走公司中转站，Embedding 走本地 BGE）

> 公司中转站 `http://192.168.18.80:3000/v1` 只提供 LLM/视觉模型，**不提供 embedding 模型**
> （实测 bge-m3 / text-embedding-3-small 等全部 503），因此向量检索改用**本地 BGE**，文档文本不出内网。

### 7.0 安装本地 embedding 依赖 + 下载模型（一次性）

```powershell
$env:HTTP_PROXY = "http://127.0.0.1:7897"
$env:HTTPS_PROXY = "http://127.0.0.1:7897"
# CPU 版 torch（避免下载几 GB 的 CUDA 版）
.venv\Scripts\python -m pip install torch --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple
# sentence-transformers（含 transformers / scipy 等）
.venv\Scripts\python -m pip install -e ".[local]"
# 下载 BGE 模型到本地（走 hf-mirror 国内镜像，约 400MB）
.venv\Scripts\python scripts\fetch_model.py
```

模型会下载到 `data/models/bge-base-zh-v1.5/`（已在 .gitignore 中，不提交；`data/` 整个目录都不入库）。
`.env` 里 `RAGKB_EMBEDDING_MODEL=data/models/bge-base-zh-v1.5` 指向这个本地路径，运行完全离线。

### 7.1 配置 `.env`

`.env` 已配好（本机当前配置）：LLM/VLM 走中转站，Embedding 走本地 BGE：

```ini
RAGKB_LLM_PROVIDER=openai-compatible
RAGKB_LLM_BASE_URL=http://192.168.18.80:3000/v1
RAGKB_LLM_API_KEY=sk-...
RAGKB_LLM_MODEL=deepseek-v4-pro-0813

RAGKB_EMBEDDING_PROVIDER=local
RAGKB_EMBEDDING_MODEL=data/models/bge-base-zh-v1.5

RAGKB_VLM_PROVIDER=openai-compatible
RAGKB_VLM_BASE_URL=http://192.168.18.80:3000/v1
RAGKB_VLM_API_KEY=sk-...
RAGKB_VLM_MODEL=deepseek-v4-flash-vision-exp
```

### 7.2 启动（用新窗口，确保没有 fake 环境变量）

```powershell
cd D:\Code\AI\RAG
.venv\Scripts\python -m uvicorn apps.api.main:app --reload
```

首次调 `/ask` 或 `ingest` 时本地 BGE 模型会加载（几秒~十几秒，只在首次），随后正常检索。

### 7.3 验证

- 摄入文档后提问：答案应为真实模型生成（不再是 `This is a fake answer.`），引用为真实向量检索结果。
- 快速自检：`/health` 里 `llm_provider=openai-compatible`、`embedding_provider=local`。

---

## 8. 问题记录（发现的问题往这里补）

| 日期 | 步骤 | 现象/报错（命令 + 完整输出） | 状态 |
|---|---|---|---|
| 2026-08-26 | 0 | `.venv\Scripts\activate` 报「无法加载模块 .venv」 | 已解决：改用 `.venv\Scripts\python` 直接执行 |
| 2026-08-26 | 4.1 | `curl.exe -d '{"username":...}'` 报 `json_invalid`（JSON 双引号被 PowerShell 吞掉） | 已解决：JSON 请求改用 `Invoke-RestMethod` |
| 2026-08-26 | 4.3/4.5 | `Invoke-RestMethod -Body` 传中文 question 被存成 `???? GPIO ???` | 已解决：JSON 先 `[System.Text.Encoding]::UTF8.GetBytes()` 转字节再传 |
| 2026-08-26 | 5 | CLI 报 `ConfigurationError: Embedding API key is not configured` | 已解决：跑 CLI 前先 `$env:RAGKB_LLM_PROVIDER="fake"`、`$env:RAGKB_EMBEDDING_PROVIDER="fake"`（backup 除外） |
| 2026-08-26 | 6 | `docker compose up` 报「无法将 docker 项识别为 cmdlet」 | 本机未安装 Docker Desktop；此节可选，装 Docker 后再测或跳过 |
| 2026-08-26 | 7 | 公司中转站无 embedding 模型（bge-m3 / text-embedding-3-small 等全部 503） | 已解决：改用本地 BGE（`RAGKB_EMBEDDING_PROVIDER=local`），文档文本不出内网 |
| 2026-08-26 | 7 | `huggingface_hub` 下载模型失败（重定向校验报错 + 大文件断连） | 已解决：新增 `scripts/fetch_model.py`，走 hf-mirror + `Range` 断点续传 + 自动重试 |
| 2026-08-26 | 7 | sentence-transformers 6.0 加载 bge-base-zh-v1.5 报 `Pooling.__init__() missing embedding_dimension` | 已解决：模型缺子目录 `1_Pooling/config.json`，tree 接口需 `?recursive=true` 才会列出子目录文件 |
| 2026-08-26 | 7 | 切换 embedding（fake 256 维 → BGE 768 维）后检索维度不匹配 | 已解决：必须重建向量库（备份旧库 → 删 `data/ragkb.sqlite` → 重新 `ingest`） |
| 2026-08-26 | 摄入5766 | 多页 PDF 丢数据：18 页 datasheet 只入库 5 块（1004→977，其余被覆盖） | 已解决：分块 ID 未含页码，各页 `chunk_index` 冲突；`splitter.py`/`code_splitter.py` 的 ID 已纳入 `page` |
| 2026-08-26 | 摄入5766 | 删库重摄后混入历史数据（`SCH_Schematic_new.pdf`，T113 开发板原理图） | 已解决：残留的 `uvicorn --reload` 进程占着旧 DB；`Stop-Process` 杀掉残留 python 进程后重摄 |
| 2026-08-26 | embedding选型 | 通义千问 embedding 测试：`qwen3.7-text-embedding` 可用（1024 维，跨语言好）；`tongyi-embedding-vision-flash`/`qwen3-vl-embedding` 报 404 | 已确认：后两者是视觉 embedding，不走 OpenAI 兼容接口；文本 RAG 用 `qwen3.7-text-embedding` |
| 2026-08-26 | embedding选型 | qwen3.7 批量上限 20 条/请求（batch=50 报 `batch size should not be larger than 20`），摄入 1000+ 块一次发会失败 | 已解决：`OpenAICompatibleEmbedding` 加分批（`RAGKB_EMBEDDING_BATCH_SIZE=20`），新增单测 |
| 2026-08-26 | 检索 | 加中文《SDK开发指南》后，`top_k=4` 时「SAR ADC 触摸按键」问被挤出去（英文 datasheet 排不上） | 已解决：`RAGKB_RETRIEVAL_TOP_K=6` 后恢复正确；18 个测试案例全部通过 |
| 2026-08-26 | 引用核验 | 「引用来源」列表把检索到的 6 块全列出，但答案正文只标了 1-3 条，其余是目录页/无关章节等无效候选（如 RT-Thread 题 6 条里只有 1 条相关） | 已解决：`RAGPipeline` 只返回正文实际引用 `[n]` 的来源，并同步重写编号保持一致（新增单测） |
| 2026-08-26 | 4.7 | 用 PowerShell `Invoke-RestMethod -Body` 传中文分类名（`芯片SDK`）被存成 `??SDK` | 已解决：含中文的 body 必须 `[System.Text.Encoding]::UTF8.GetBytes()` 转字节再传（同 4.3）；或直接用 `scripts/seed_categories.py` 建分类 |
