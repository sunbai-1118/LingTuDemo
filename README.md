# LingTuDemo — 用户认证 + RBAC + AI 用户名审核

一个面向技术面试的 Web Demo：用户注册 / 登录（JWT）+ USER/ADMIN 角色权限（Resource A / B）+ 注册时由 LLM 审核用户名（结构化输出、防注入、失败即拒绝）。

## 功能特性

- **注册 / 登录**：JWT 认证，密码使用 Argon2 哈希存储。
- **RBAC 权限控制**：USER 仅可访问 Resource A，ADMIN 可访问 Resource A / B，权限由后端强制校验。
- **AI 用户名审核**：注册时由 LLM 审核用户名，强制结构化输出、防 Prompt 注入、审核失败即拒绝注册（fail closed）。

## 实现方式

- **后端**：FastAPI 分层架构（Router → Service → Repository → Model），JWT 认证，后端强制 RBAC。
- **前端**：Vue 3 + TypeScript + naive-ui，登录 / 注册 / Dashboard 三个页面，处理 Loading、表单校验、401/403、Token 过期等状态。
- **AI 审核**：注册流程中调用 OpenAI 兼容接口对用户名做审核，强制 JSON 结构化输出，仅信任 `allowed` 字段；用户名作为"数据"传入，防 Prompt 注入；LLM 任何失败都会拒绝本次注册（fail closed）。
- **部署**：Docker Compose 一键启动 frontend (Nginx) / backend / mysql。

## 整体架构

```text
浏览器 (Vue3 SPA)
   │  /api/*  (Nginx 反向代理)
   ▼
FastAPI backend
   ├── api/        Router：HTTP 层（auth、resources）
   ├── services/   业务逻辑（LLM 用户名审核）
   ├── repositories/ 数据库访问
   ├── models/     SQLAlchemy 模型（users 表）
   ├── schemas/    Pydantic 请求/响应结构
   └── core/       配置、JWT、密码哈希、认证依赖
   ▼
MySQL 8 (users 表)

注册流程：参数校验 → 用户名重复检查 → LLM 审核 → 结构化结果 → 允许则建号 / 拒绝则报错
```

## 技术栈

- **Frontend**：Vue 3、TypeScript、Vite、Vue Router、Pinia、Axios、naive-ui
- **Backend**：Python 3.12、FastAPI、SQLAlchemy 2、Pydantic v2、PyJWT、pwdlib(Argon2)、OpenAI SDK
- **Database**：MySQL 8
- **Deployment**：Docker、Docker Compose、Nginx

## 设计出发点

1. **安全优先**：密码只存哈希（Argon2）；JWT 携带 user_id/role/exp；身份永远从 Token 解析，不信任前端任何角色信息；前端隐藏按钮只是 UI 优化，真正的拦截在后端（Resource B：USER → 403）。
2. **AI 是流程的一部分而非装饰**：LLM 审核是注册链路的一个必经步骤，失败时拒绝注册而不是放行。
3. **简单可靠**：单表 users、无多余中间件、无过度设计；每层职责清晰。

## LLM 用户名审核设计

- 强制 JSON 结构化输出，仅信任 `allowed` 字段；`allowed=true` 时 `category` 必须为 `normal`。
- 将用户名视为待审核数据并明确声明其"绝非指令"，防止 Prompt 注入；`temperature=0` 保证结果确定性。
- `category` 固定枚举：`normal` / `profanity` / `porn` / `violence` / `hate` / `other`。
- 批测 **13/13 通过**：正常中英文、数字、游戏昵称、特殊符号及边界昵称（如"屁桃君"）均放行；注入话术与侮辱 / 色情 / 仇恨 / 引流内容均被拒绝且类别正确。

## 项目部署方式

### Docker Compose（推荐）

```bash
cp .env.example .env   # 填入 JWT_SECRET、LLM_API_KEY 等
docker compose up -d
# 访问 http://localhost
```

包含 4 个服务：`frontend`（Nginx 托管 SPA + 反代 /api）、`backend`（FastAPI:8000）、`mysql`（MySQL 8 + 数据卷）、启动时自动建表并播种管理员账号。

### 本地开发

```bash
# 后端
cd backend && python -m venv .venv && .venv/Scripts/pip install -r requirements.txt
cp .env.example .env   # 改 DATABASE_URL 端口等
.venv/Scripts/uvicorn app.main:app --port 8000

# 前端
cd frontend && npm install && npm run dev   # http://localhost:5173，/api 代理到 8000

# 测试
cd backend && .venv/Scripts/python -m pytest tests -q
```

## 测试账号

| 角色 | 用户名 | 密码 | 权限 |
|---|---|---|---|
| ADMIN | `admin` | `admin12345` | Resource A ✓ / Resource B ✓ |
| USER | 自行注册（如 `xiaoming2024`） | 注册时设置 | Resource A ✓ / Resource B 🔒 |

管理员账号由后端启动时自动播种（可用 `ADMIN_USERNAME` / `ADMIN_PASSWORD` 环境变量覆盖）。

## API 一览

```text
POST /api/auth/register   注册（LLM 审核用户名）
POST /api/auth/login      登录，返回 JWT
GET  /api/auth/me         当前用户信息（需 Token）
GET  /api/resources/a     所有登录用户可访问
GET  /api/resources/b     仅 ADMIN（USER→403，未登录→401）
GET  /api/health          健康检查
```

统一响应结构：`{"code": 200, "message": "success", "data": {...}}`。
