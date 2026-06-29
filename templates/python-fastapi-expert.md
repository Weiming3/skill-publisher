---
name: python-fastapi-expert
description: "当用户为 FastAPI 项目生成 / 修改代码时使用此 skill,按团队规范生成路由分组(APIRouter + 统一前缀 /api/v1)、请求响应模型(Pydantic)、统一响应格式({code, msg, data})、异常处理(全局 ExceptionHandler)、依赖注入(get_db 等复用)。支持 FastAPI 0.100+,Pydantic v2。当用户提到「FastAPI 规范」「Python 后端规范」「API 设计」「FastAPI 编码风格」「Pydantic 模型」等关键词时使用。不适用于:(1) Django / Flask 项目(用对应 skill);(2) 纯异步任务队列(那是 Celery / arq 范畴);(3) 微服务框架(如 Nameko)。"
license: Apache 2.0
---

# Python FastAPI Expert(FastAPI 后端开发规范)

你是 **FastAPI 后端开发规范专家**,让 AI 按团队约定的**路由组织 / 请求响应 / 异常处理 / 依赖注入**生成代码。

## 核心能力

### 1. 路由组织
- 按业务模块拆分 `routers/<module>.py`
- 使用 `APIRouter` 分组,统一前缀 `/api/v1/<module>`
- 路由函数用动词 + 名词(`GET /users/{id}`)

### 2. 请求响应模型
- 用 Pydantic `BaseModel` 定义请求 / 响应
- `Field` 加校验(最小长度 / 正则 / 范围)
- 响应模型用 `response_model=`
- 路径参数用 `Path()` 校验

### 3. 统一响应格式
```json
{ "code": 0, "msg": "ok", "data": { ... } }
```
- `code=0` 成功,非 0 失败
- `msg` 用户可读消息
- `data` 实际数据(失败时为 null)

### 4. 异常处理
- 全局 `@app.exception_handler(BusinessError)`
- 捕获已知异常,返回统一格式
- 不暴露内部堆栈到客户端
- 业务异常 `BusinessError(status_code, code, msg)`

### 5. 依赖注入
- 复用 `get_db` / `get_current_user` / `get_redis`
- Service 层通过 `Depends()` 注入
- 数据库 session 用 generator (`yield` + `finally: close`)

## 关键规则

### 必须遵守
- ✅ 路由用 `APIRouter` 分组
- ✅ 请求 / 响应必须有 Pydantic 模型
- ✅ 路径参数必须类型注解(`user_id: int`)
- ✅ 业务异常用 `BusinessError`
- ✅ 全局异常处理捕获所有已知异常
- ✅ 数据库 session 用 `Depends(get_db)`
- ✅ 异步路由 `async def`
- ✅ 关键操作记录日志(`logger.info`)

### 禁止
- ❌ 路由函数无类型注解
- ❌ 业务逻辑写在路由函数里(放 service)
- ❌ 返回裸 dict(用 `ResponseModel`)
- ❌ 异常堆栈暴露到客户端
- ❌ 用 `*args` / `**kwargs` 当 API 参数
- ❌ 同步阻塞 I/O 在 async 函数里

## 工作流程

### 第一步:扫描项目
```
app/
├── main.py           # FastAPI app
├── routers/
│   ├── user.py
│   └── order.py
├── schemas/          # Pydantic
├── services/         # 业务
├── repositories/     # DB
├── deps.py           # 依赖
└── core/
    ├── exceptions.py
    └── response.py
```

### 第二步:生成代码模板

**Router**:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserOut
from app.services.user import UserService
from app.core.response import success, error

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut)
async def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """创建用户。

    - 需要登录
    - username 全局唯一
    """
    try:
        user = UserService(db).create(payload, current_user.id)
        return success(user)
    except ValueError as e:
        return error(code=4001, msg=str(e))
```

**Schema (Pydantic v2)**:
```python
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}  # for ORM mode
```

**Service**:
```python
from sqlalchemy.orm import Session

from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserOut


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def create(self, payload: UserCreate, creator_id: int) -> UserOut:
        if self.repo.find_by_username(payload.username):
            raise ValueError("用户名已存在")
        user = self.repo.create(payload)
        self.db.commit()
        return UserOut.model_validate(user)

    def get_by_id(self, user_id: int) -> UserOut:
        user = self.repo.find_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        return UserOut.model_validate(user)
```

**Deps**:
```python
from typing import Generator

from sqlalchemy.orm import Session

from app.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 第三步:统一异常处理

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class BusinessError(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg


app = FastAPI()


@app.exception_handler(BusinessError)
async def business_handler(request: Request, exc: BusinessError):
    return JSONResponse(
        status_code=200,  # 业务错仍返回 200,用 code 区分
        content={"code": exc.code, "msg": exc.msg, "data": None},
    )


@app.exception_handler(Exception)
async def global_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=500,
        content={"code": 5000, "msg": "服务器内部错误", "data": None},
    )
```

## 使用示例

### 示例 1:写 CRUD

```python
@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    return success(UserService(db).get_by_id(user_id))


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return success(UserService(db).update(user_id, payload))
```

### 示例 2:批量扫描

```bash
$ python scripts/fastapi_audit.py --path ./app
[🔴] routers/legacy.py:42 — 路由无类型注解
[🟡] services/user.py:88 — 业务逻辑写在路由
[🟢] routers/order.py — 全部合规
```

## 注意事项

### 常见误区
- ❌ 路由返回 `dict` → 用 Pydantic `response_model`
- ❌ `try/except` 在路由里 → 全局异常处理
- ❌ 同步 SQLAlchemy 在 async 路由 → 性能问题,改 `asyncpg` 或线程池

### 关键警告
⚠️ Pydantic v2 与 v1 API 不同,`model_validate` ≠ `from_orm`
⚠️ `Depends(get_db)` 必须 yield 才能正确关闭
⚠️ 异常堆栈**绝不**返回到客户端(只 log)

## 参考资源
- [FastAPI 官方文档](https://fastapi.tiangolo.com/zh/)
- [Pydantic v2 文档](https://docs.pydantic.dev/latest/)
- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/en/20/)
- [Full Stack FastAPI Template](https://github.com/tiangolo/full-stack-fastapi-template)