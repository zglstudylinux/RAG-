# RAG 知识库系统 — 完整安装、测试与排错文档

> 在 VMware Ubuntu 24.04 虚拟机内,通过 Docker 部署 [zglstudylinux/RAG-](https://github.com/zglstudylinux/RAG-) 项目的全流程指南。
> 包含**正常安装步骤**、**验证测试**、以及**实测踩坑后的排错手册**。

---

## 0. 环境信息(本文实测)

| 项目 | 值 |
|------|-----|
| 宿主机 | Windows + VMware |
| 虚拟机 | Ubuntu 24.04.4 LTS (Noble) |
| 内核 | 7.0.0-28-generic |
| VM IP | `192.168.32.6`(ens33,`ip -4 addr show` 查得) |
| 代理 | `http://192.168.32.153:7897`(宿主机代理,已允许局域网连接) |
| 用户 | `zgl`,已具备 sudo 权限 |
| Docker 版本 | Engine 29.7.2 + Compose v5.5.0 |
| 服务端口 | `8000`(容器 `0.0.0.0:8000 -> 8000`) |
| 默认账号 | `admin` / `admin123` |
| 访问地址 | `http://192.168.32.6:8000/` |

> ⚠️ 你的 IP、代理地址可能不同,请按 `ip addr` 实际值替换。下文统一用 `<VM-IP>` 与 `<PROXY>` 表示。

---

## 1. 为什么在 VM Linux 里跑 Docker

- **Linux 原生跑 Docker**:不用 WSL / 不用管理员 / 不用重启 Windows。
- 比 Windows 上装 Docker Desktop 省事得多,资源占用也更低。
- VMware NAT 网络模式下,VM 通常可直接上外网;若需走宿主机代理,把代理指向宿主机 IP 并允许局域网连接即可。

---

## 2. 安装前准备

### 2.1 确认 VM 能连外网(直连或走代理)

```bash
# 直连测试
curl -sI --max-time 5 https://www.google.com | head -1

# 若需走宿主机代理(本文场景):
curl -s --max-time 5 -x http://192.168.32.153:7897 https://www.google.com -o /dev/null -w "proxy_status:%{http_code}\n"
# 期望输出 proxy_status:200 或 302
```

如果代理不通,先在宿主机代理软件里**打开"允许局域网连接"**,并确认 `192.168.32.153:7897` 这个 IP:端口确实是代理监听地址。

### 2.2 记录关键信息

```bash
# VM IP
ip -4 addr show | grep "inet " | grep -v 127.0.0.1
# 本文输出: inet 192.168.32.6/24 ... ens33

# 系统版本
lsb_release -a      # 或 cat /etc/os-release
```

### 2.3 安装 git(若未安装)

```bash
sudo apt update && sudo apt install -y git
```

---

## 3. 配置代理(本文关键,影响 apt/docker/git/pip)

代理分**三处**生效,缺一不可:

1. **当前 shell + `~/.bashrc`**:给 `curl`/`git clone`/手动命令用。
2. **`apt` 配置**:给 `apt install` 用(apt 不读 `http_proxy` 环境变量,要单独配)。
3. **Docker daemon + Docker build**:给 `docker pull`/`docker build` 用(见第 5、6 节)。

### 3.1 当前会话 + 持久化(`~/.bashrc`)

```bash
cat >> ~/.bashrc <<'EOF'

# === Proxy 192.168.32.153:7897 ===
export http_proxy=http://192.168.32.153:7897
export https_proxy=http://192.168.32.153:7897
export HTTP_PROXY=http://192.168.32.153:7897
export HTTPS_PROXY=http://192.168.32.153:7897
export no_proxy=localhost,127.0.0.1,::1,192.168.32.0/24
export NO_PROXY=localhost,127.0.0.1,::1,192.168.32.0/24
# === end proxy ===
EOF

# 当前会话立即生效(或在后续每个 Bash 命令前手动 export)
export http_proxy=http://192.168.32.153:7897
export https_proxy=http://192.168.32.153:7897
export HTTP_PROXY=http://192.168.32.153:7897
export HTTPS_PROXY=http://192.168.32.153:7897
export no_proxy=localhost,127.0.0.1,::1,192.168.32.0/24
export NO_PROXY=localhost,127.0.0.1,::1,192.168.32.0/24

# 验证
env | grep -i proxy
```

> `no_proxy` 必须包含本网段 `192.168.32.0/24`,否则 VM 内部、容器互访也会绕去走代理而失败。

### 3.2 apt 代理

```bash
sudo tee /etc/apt/apt.conf.d/95proxy > /dev/null <<'EOF'
Acquire::http::Proxy "http://192.168.32.153:7897";
Acquire::https::Proxy "http://192.168.32.153:7897";
Acquire::ftp::Proxy "http://192.168.32.153:7897";
EOF

# 验证
sudo apt update
```

### 3.3 系统级 profile(可选,让所有登录 shell 都有代理)

```bash
sudo tee /etc/profile.d/proxy.sh > /dev/null <<'EOF'
export http_proxy=http://192.168.32.153:7897
export https_proxy=http://192.168.32.153:7897
export HTTP_PROXY=http://192.168.32.153:7897
export HTTPS_PROXY=http://192.168.32.153:7897
export no_proxy=localhost,127.0.0.1,::1,192.168.32.0/24
export NO_PROXY=localhost,127.0.0.1,::1,192.168.32.0/24
EOF
sudo chmod +x /etc/profile.d/proxy.sh
```

---

## 4. 安装 Docker Engine + compose 插件

### 4.1 官方一键脚本安装

```bash
# 注意:sudo 默认会清除环境变量,导致脚本内的 curl/apt 不走代理 → 会超时失败。
# 解决:用 sudo -E 保留环境变量,并在子 shell 里再次 export 代理。
sudo -E sh -c '
export http_proxy=http://192.168.32.153:7897
export https_proxy=http://192.168.32.153:7897
export HTTP_PROXY=http://192.168.32.153:7897
export HTTPS_PROXY=http://192.168.32.153:7897
curl -fsSL https://get.docker.com -o /tmp/get-docker.sh && sh /tmp/get-docker.sh
'
```

脚本会自动通过 apt 安装 `docker-ce`、`docker-ce-cli`、`containerd.io`、`docker-compose-plugin`、`docker-buildx-plugin` 等。**首次需联网下载,约 3~6 分钟。**

### 4.2 把当前用户加入 docker 组(免 sudo)

```bash
sudo usermod -aG docker $USER
newgrp docker          # 立即生效(或重新登录一次)
```

> 加组后,当前已打开的 shell 仍需 `newgrp docker` 或重开终端才会免 sudo。本文后续命令在未免 sudo 前一律带 `sudo`。

### 4.3 启动并验证

```bash
sudo systemctl enable --now docker
sudo systemctl is-active docker          # 期望: active

docker --version                         # Docker version 29.7.2
docker compose version                   # Docker Compose version v5.5.0

sudo docker info --format 'Server={{.ServerVersion}} Storage={{.Driver}} Cgroup={{.CgroupDriver}}'
# 期望: Server=29.7.2 Storage=overlayfs Cgroup=systemd
```

---

## 5. 配置 Docker 代理(拉镜像用)

### 5.1 Docker daemon 代理(systemd drop-in)

让 `docker pull` 拉取镜像时走代理:

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf > /dev/null <<'EOF'
[Service]
Environment="HTTP_PROXY=http://192.168.32.153:7897"
Environment="HTTPS_PROXY=http://192.168.32.153:7897"
Environment="NO_PROXY=localhost,127.0.0.1,::1,192.168.32.0/24"
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证
sudo systemctl show docker --property=Environment
# 期望看到 HTTP_PROXY=... HTTPS_PROXY=...
```

### 5.2 配置国内镜像源(强烈推荐,避免 docker.io 拉取超时)

```bash
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://mirror.ccs.tencentyun.com"
  ]
}
EOF

sudo systemctl restart docker
sleep 3
sudo systemctl is-active docker          # 期望: active
```

### 5.3 测试拉取基础镜像

```bash
sudo docker pull python:3.11-slim
# 期望: Status: Downloaded newer image for python:3.11-slim
```

---

## 6. 克隆项目代码

```bash
cd ~                    # 本文用 ~/Docker 作为工作目录
mkdir -p ~/Docker && cd ~/Docker

# git clone 显式指定代理
git -c http.proxy=http://192.168.32.153:7897 \
    -c https.proxy=http://192.168.32.153:7897 \
    clone https://github.com/zglstudylinux/RAG-.git

cd RAG-
ls -la                  # 应看到 Dockerfile、docker-compose.yml、pyproject.toml、apps/、packages/ 等
```

### 6.1 关键文件说明

| 文件 | 作用 |
|------|------|
| `Dockerfile` | 构建镜像:基于 `python:3.11-slim`,`pip install .`,暴露 8000 端口 |
| `docker-compose.yml` | 服务编排:build → 端口 8000、挂载 `ragkb-data` 卷、注入环境变量 |
| `.env.example` | 环境变量模板(LLM/Embedding provider、JWT、admin 密码等) |
| `.dockerignore` | 构建时排除 `.venv`/`tests`/`data`/`.env` 等 |
| `pyproject.toml` | Python 依赖声明(fastapi、jieba、openai、pymupdf 等) |

### 6.2 准备 `.env`(离线可启动)

`.env.example` 默认是 `openai-compatible`(需 API key)。**先用 fake provider 确保无 key 也能启动:**

```bash
cp -n .env.example .env

# 改成 fake provider(离线确定性 provider,用于测试/演示)
sed -i 's/^RAGKB_LLM_PROVIDER=openai-compatible/RAGKB_LLM_PROVIDER=fake/' .env
sed -i 's/^RAGKB_EMBEDDING_PROVIDER=openai-compatible/RAGKB_EMBEDDING_PROVIDER=fake/' .env

# 确认关键项
grep -E "^RAGKB_LLM_PROVIDER=|^RAGKB_EMBEDDING_PROVIDER=|^RAGKB_DEFAULT_ADMIN_PASSWORD=|^RAGKB_JWT_SECRET=" .env
```

期望输出:
```
RAGKB_LLM_PROVIDER=fake
RAGKB_EMBEDDING_PROVIDER=fake
RAGKB_DEFAULT_ADMIN_PASSWORD=admin123
RAGKB_JWT_SECRET=change-me-in-production-use-a-long-random-secret
```

> 生产环境再改回 `openai-compatible` 并填真实 API key,见第 9 节。

---

## 7. 构建并启动服务

### 7.1 修改 Dockerfile(加 PyPI 国内镜像,见第 8 节踩坑)

为确保 `pip install .` 顺利,把 `Dockerfile` 改为:

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

WORKDIR /app

COPY pyproject.toml ./
COPY packages ./packages
COPY apps ./apps

# 清空构建期代理: pip 直连国内镜像,避免上游 HTTP 代理损坏大体积 sdist(jieba 19MB)
# 导致 sha256 校验失败。最终运行容器无需代理。
ENV http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY=

RUN pip install .

EXPOSE 8000

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> 这一行 `ENV http_proxy= ...` 是解决 jieba 哈希校验失败的**关键**,原因见第 8.1 节。

### 7.2 构建 + 启动

```bash
cd ~/Docker/RAG-

# 构建并后台启动(首次构建需联网下载 pip 依赖,约 3~5 分钟)
sudo docker compose up --build -d

# 若已构建过镜像,只需:
sudo docker compose up -d
```

### 7.3 查看状态与日志

```bash
sudo docker compose ps                       # 容器状态
sudo docker compose logs -f                  # 实时日志(Ctrl+C 退出)
sudo docker compose logs --tail 20          # 最近 20 行
```

期望容器 `STATUS` 为 `Up ...`,端口 `0.0.0.0:8000->8000/tcp`。

---

## 8. 验证测试

### 8.1 健康检查 `/health`

```bash
# 本机回环
curl -s http://127.0.0.1:8000/health | python3 -m json.tool

# 用 VM IP(验证对外可达)
curl -s http://192.168.32.6:8000/health | python3 -m json.tool
```

期望返回:
```json
{
  "status": "ok",
  "service": "ragkb",
  "version": "1.0.0",
  "config": {
    "env": "dev",
    "llm_provider": "fake",
    "embedding_provider": "fake",
    "vlm_provider": "none",
    "store_path": "/data/ragkb.sqlite",
    "retrieval_mode": "hybrid",
    ...
  }
}
```

### 8.2 首页

```bash
curl -s -o /dev/null -w "homepage_http:%{http_code}\n" http://192.168.32.6:8000/
# 期望: homepage_http:200
```

### 8.3 登录接口(账号 admin / admin123)

```bash
# 先从 OpenAPI 确认路径
curl -s http://127.0.0.1:8000/openapi.json \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(m.upper(),p) for p,v in d.get('paths',{}).items() for m in v]" \
  | grep -iE "login|auth"

# 登录
curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

期望返回含 `token`、`username`、`role` 的 JSON:
```json
{"token":"eyJ...","username":"admin","role":"admin"}
```

### 8.4 从 Windows 浏览器访问

在 Windows 浏览器打开(注意是 VM IP,不是 127.0.0.1):

```
http://192.168.32.6:8000/
```

用 `admin` / `admin123` 登录即可进入系统界面。

> 若打不开:确认 VM 防火墙未拦 8000(`sudo ufw status`;若 enabled,`sudo ufw allow 8000`),以及 VMware 网络是 NAT 或桥接且 Windows 与 VM 网络可达(`ping 192.168.32.6`)。

---

## 9. 切换到真实 LLM / Embedding(可选,fake → 在线)

fake provider 仅用于离线跑通流程。要真正做 RAG 问答/向量检索,改 `.env`:

```bash
cd ~/Docker/RAG-

# 编辑 .env,改成真实 provider
# LLM: DeepSeek 示例
#   RAGKB_LLM_PROVIDER=openai-compatible
#   RAGKB_LLM_BASE_URL=https://api.deepseek.com/v1
#   RAGKB_LLM_API_KEY=sk-你的key
#   RAGKB_LLM_MODEL=deepseek-chat
#
# Embedding: SiliconFlow 示例
#   RAGKB_EMBEDDING_PROVIDER=openai-compatible
#   RAGKB_EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
#   RAGKB_EMBEDDING_API_KEY=sk-你的key
#   RAGKB_EMBEDDING_MODEL=BAAI/bge-m3
nano .env        # 或 vim

# 改完重启(无需重新 build,因为是环境变量注入)
sudo docker compose up -d

# 再次健康检查,确认 llm_provider/embedding_provider 已切换
curl -s http://127.0.0.1:8000/health | python3 -m json.tool | grep -E "llm_provider|embedding_provider"
```

---

## 10. 排错手册(实测踩坑汇总)

按"现象 → 原因 → 解决"组织,均为本文实测遇到的真实问题。

### 10.1 `sudo curl` / `sudo sh get-docker.sh` 不走代理,报 `Connection reset` / 超时

**现象**
```
curl: (35) Recv failure: Connection reset by peer
# 或
dial tcp ...:443: i/o timeout
```

**原因**:`sudo` 默认会**清除环境变量**(安全策略 `env_reset`),所以即使你在普通 shell 里 `export http_proxy=...`,进了 `sudo` 子进程后这些变量没了,`curl`/`apt` 直连外网而失败。

**解决**:用 `sudo -E` 保留环境变量,并在子 shell 内再次 `export`:
```bash
sudo -E sh -c '
  export http_proxy=... https_proxy=... HTTP_PROXY=... HTTPS_PROXY=...
  curl -fsSL https://get.docker.com -o /tmp/get-docker.sh && sh /tmp/get-docker.sh
'
```

### 10.2 `docker pull python:3.11-slim` 报 `failed to fetch anonymous token ... i/o timeout`

**现象**
```
ERROR: failed to authorize: failed to fetch anonymous token:
Get "https://auth.docker.io/token?...": dial tcp 174.36.196.242:443: i/o timeout
```

**原因**:`auth.docker.io` 在国内访问不稳定/超时;即使配了 daemon 代理,直连 docker.io 仍可能失败。

**解决**:配置国内 registry 镜像源(第 5.2 节),`daemon.json` 填 `registry-mirrors` 后 `systemctl restart docker`,再 `docker pull`。

### 10.3 `pip install .` 报 `THESE PACKAGES DO NOT MATCH THE HASHES`(jieba)

**现象**
```
ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE.
    jieba>=0.42.1 ... :
        Expected sha256 055ca12f...
             Got        e83ed53385...
```

**原因**:这是本项目的**核心坑**。`jieba-0.42.1.tar.gz` 约 19MB,当 pip **经由 HTTP 代理(7897)下载大体积 sdist** 时,代理对大文件流的处理会损坏部分字节,导致下载内容 `sha256` 与 PyPI 记录不符 → 校验失败。代理对小包(几十 KB)通常没事,但大 sdist 容易踩雷。

**解决**:让构建容器内的 pip **绕过代理、直连国内 PyPI 镜像**:

1. Dockerfile 加清华源:
   ```dockerfile
   ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
       PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
   ```
2. 在 `RUN pip install .` **之前**清空构建层代理:
   ```dockerfile
   ENV http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY=
   ```
   这一步至关重要——Docker build 的代理来自 `~/.docker/config.json` 的 `proxies` 字段,会被自动注入到每个 `RUN` 容器;若不清空,pip 仍会走 7897 代理 → 依旧损坏。

> ⚠️ 注意区分两条代理路径:
> - **buildkit 拉基础镜像**(`python:3.11-slim`)→ 用 daemon 的 systemd 代理 / registry 镜像,要保持。
> - **RUN 层内 pip 装包** → 必须清空代理,直连国内 PyPI。

### 10.4 改了 Dockerfile 但 build 仍走代理(jieba 仍报哈希错)

**原因**:`~/.docker/config.json` 里的 `proxies.default` 会被自动注入所有 build 容器,**覆盖**你在 Dockerfile 里 `ENV http_proxy=` 的意图有时不生效,或排查时不确定。

**临时排查方法**:先把 build 代理 config 移开再构建,确认问题确实在代理:
```bash
mv ~/.docker/config.json ~/.docker/config.json.bak
sudo docker compose build       # 验证 pip 是否直连成功
mv ~/.docker/config.json.bak ~/.docker/config.json   # 验证后恢复(拉基础镜像还要用)
```
最终方案是第 10.3 的"清空 ENV"——两全其美:基础镜像仍走 daemon 代理,RUN 层 pip 直连国内源。

### 10.5 容器起来了但 Windows 浏览器打不开 `http://<VM-IP>:8000/`

依次排查:

1. **VM 内本机是否通**:
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/health   # 应 200
   curl -s http://192.168.32.6:8000/health                                  # 应能通
   ```
   若本机通、外网不通 → 防火墙/网络问题;若本机也不通 → 容器或应用问题。

2. **端口是否真的映射**:
   ```bash
   sudo docker compose ps      # 看 PORTS 列是否有 0.0.0.0:8000->8000
   sudo ss -tlnp | grep 8000   # 宿主机是否监听 8000
   ```

3. **VM 防火墙**:
   ```bash
   sudo ufw status
   # 若 Status: active,放行:
   sudo ufw allow 8000
   ```

4. **Windows ↔ VM 网络**:
   ```cmd
   ping 192.168.32.6          # 在 Windows cmd 里 ping VM IP
   ```
   不通则检查 VMware 网络模式(NAT/桥接)与 Windows 防火墙。

5. **VMware NAT 模式**:Windows 访问 VM 需保证 VM 的 IP 与 Windows 在同一可达网段。NAT 下 VM IP 形如 `192.168.x.x`,Windows 通过 VMware 虚拟网卡(vmnet8)可达;桥接模式则 VM 与 Windows 同物理网段。

### 10.6 登录返回 404 `{"detail":"Not Found"}`

**原因**:登录路径不是 `/api/auth/login` 而是 `/auth/login`。

**解决**:先查 OpenAPI 确认正确路径:
```bash
curl -s http://127.0.0.1:8000/openapi.json \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(m.upper(),p) for p,v in d.get('paths',{}).items() for m in v]" | grep -i auth
```
本项目为 `POST /auth/login`、`GET /auth/me`。

### 10.7 容器频繁退出 / 重启循环

```bash
sudo docker compose ps -a                    # 看 STATUS 是否 restarting/exited
sudo docker compose logs --tail 50           # 看退出原因
```
常见:应用启动异常、端口被占用(`sudo ss -tlnp | grep 8000` 找占用进程并停掉)、`.env` 配置错误导致 provider 初始化抛异常。

### 10.8 `docker compose` 命令需要 sudo

**原因**:虽然 `usermod -aG docker $USER` 已加组,但当前 shell 未生效(组变更要新会话才生效)。

**解决**:
```bash
newgrp docker          # 当前 shell 立即生效
# 或直接重开一个终端/重新 SSH 登录
```
之后即可直接 `docker compose ...` 免 sudo。

### 10.9 重新构建/清空重来

```bash
cd ~/Docker/RAG-
sudo docker compose down                 # 停止并删容器(保留卷)
sudo docker compose down -v               # 连数据卷一起删(数据会丢!)
sudo docker compose build --no-cache      # 不用缓存重新构建(改了 Dockerfile/pyproject 排查时用)
sudo docker compose up -d --build         # 重新构建并启动
```

---

## 11. 常用运维命令速查

```bash
cd ~/Docker/RAG-

# 生命周期
sudo docker compose up -d               # 后台启动
sudo docker compose down                # 停止并删容器(保留数据卷)
sudo docker compose down -v            # 停止并删容器+数据卷(数据丢失)
sudo docker compose restart            # 重启
sudo docker compose up -d --build       # 改代码/Dockerfile 后重新构建并启动

# 观测
sudo docker compose ps                 # 容器状态
sudo docker compose logs -f            # 实时日志
sudo docker compose logs --tail 50     # 最近 50 行
sudo docker compose top                 # 容器内进程

# 进入容器
sudo docker compose exec ragkb bash

# 镜像/卷
sudo docker images                     # 列镜像
sudo docker volume ls                   # 列卷
sudo docker system df                   # 磁盘占用
sudo docker system prune -a --volumes   # 清理未用镜像/卷(谨慎)

# 验证
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 12. 最终成果(本文实测)

```
✅ Docker 29.7.2 + Compose v5.5.0 安装成功,daemon active
✅ 用户 zgl 已加入 docker 组
✅ RAG- 项目克隆至 ~/Docker/RAG-
✅ 镜像构建成功 rag--ragkb:latest
✅ 容器 rag--ragkb-1 运行中,端口 0.0.0.0:8000->8000
✅ GET /health -> {"status":"ok","version":"1.0.0",...}
✅ GET / -> 200
✅ POST /auth/login (admin/admin123) -> 返回 JWT token
✅ Windows 浏览器 http://192.168.32.6:8000/ 可访问
```

> 当前为 **fake provider 离线模式**,可跑通整套流程与界面;真实 RAG 问答请按第 9 节配置 API key 后重启。

---

## 附录 A:完整 Dockerfile(实测可用版)

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

WORKDIR /app

COPY pyproject.toml ./
COPY packages ./packages
COPY apps ./apps

# 清空构建期代理: pip 直连国内镜像,避免上游 HTTP 代理损坏大体积 sdist(jieba 19MB)
# 导致 sha256 校验失败。最终运行容器无需代理。
ENV http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY=

RUN pip install .

EXPOSE 8000

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 附录 B:完整 daemon.json

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://mirror.ccs.tencentyun.com"
  ]
}
```
路径 `/etc/docker/daemon.json`,改完 `sudo systemctl restart docker`。

## 附录 C:涉及到的代理配置文件清单

| 文件 | 作用 | 示例内容 |
|------|------|----------|
| `~/.bashrc` | shell 环境变量 | `export http_proxy=http://192.168.32.153:7897` ... |
| `/etc/profile.d/proxy.sh` | 全局登录 shell 代理 | 同上 |
| `/etc/apt/apt.conf.d/95proxy` | apt 代理 | `Acquire::http::Proxy "http://192.168.32.153:7897";` |
| `/etc/systemd/system/docker.service.d/http-proxy.conf` | docker daemon 代理(拉镜像) | `[Service] Environment="HTTP_PROXY=..."` |
| `/etc/docker/daemon.json` | registry 镜像源 | `{"registry-mirrors":[...]}` |
| `~/.docker/config.json` | docker build 容器代理注入 | `{"proxies":{"default":{...}}}` |

> 改 IP/端口时,**以上 6 处 + `.env`** 都要同步更新。
