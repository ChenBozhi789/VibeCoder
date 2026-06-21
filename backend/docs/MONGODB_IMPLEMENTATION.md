# MongoDB 后端数据库实现思路

## 一、现状与目标

- **现状**：任务数据由 `TaskManager` 持久化到 `backend/data/task_store.json`，单文件 JSON，进程内内存 + 定时落盘。
- **目标**：用 MongoDB 作为唯一任务数据源，支持多实例部署、重启不丢数据、便于后续扩展（项目/应用元数据、用户等）。

## 二、技术选型

| 项目       | 选择        | 说明 |
|------------|-------------|------|
| 驱动       | **Motor**   | 异步驱动，与 FastAPI 的 async 风格一致；若暂时只做同步也可用 **PyMongo**。 |
| 配置       | 环境变量    | `MONGODB_URI`（必选）、可选 `MONGODB_DB_NAME`。 |
| 文档结构   | 与现有一致 | 一个 task 一个 document，字段：`task_id`, `status`, `progress`, `logs`, `result`，便于平滑迁移。 |

## 三、目录与模块划分

```
backend/
├── main.py                 # 不变，仅注入 DB 依赖（可选）
├── config.py               # 新增：读取 MONGODB_URI 等
├── db/
│   ├── __init__.py         # 暴露 get_database、get_task_repo 等
│   ├── connection.py       # 连接单例（Motor 或 PyMongo）
│   └── repositories/
│       ├── __init__.py
│       └── task_repository.py   # Task 的增删改查，封装集合访问
├── models/                 # 可选：若希望明确 schema，可放 Pydantic 或 TypedDict
│   └── task.py
├── utils/
│   └── task_manager.py     # 改为委托 task_repository + 内存缓存（可选）
└── data/                   # 保留或弃用：task_store.json 可仅作迁移/备份
```

- **connection.py**：根据 `MONGODB_URI` 建立连接，提供 `get_database()`；支持 FastAPI 的 ` lifespan` 里 `on_startup` 连接、`on_shutdown` 关闭。
- **task_repository.py**：所有对「任务」的读写都经过这里（按 `task_id` 查/改/列表），接口与当前 `TaskManager` 对齐，便于替换。
- **task_manager.py**：保留对外 API（`create_task`, `update_task`, `get_task`, `get_all_tasks`, `retrieve_task_id`），内部改为调用 `task_repository`；若需减少读库压力，可加一层进程内缓存（TTL 或按 task_id 缓存）。

## 四、集合设计

### 4.1 集合：`tasks`

| 字段       | 类型     | 说明 |
|------------|----------|------|
| `_id`      | ObjectId | 可选，若用 `task_id` 做主键可不用 `_id`。 |
| `task_id`  | string   | 业务主键，UUID，唯一索引。 |
| `status`   | string   | 枚举：pending / running / completed / failed。 |
| `progress` | int      | 0–100。 |
| `logs`     | array    | 字符串数组，追加型。 |
| `result`   | any      | 任意结构（如生成结果路径、错误信息等）。 |
| `created_at` | datetime | 可选，便于按时间排序、清理。 |
| `updated_at` | datetime | 可选，便于排查与审计。 |

- **索引**：`task_id` 唯一索引；按时间查时可加 `created_at` 或 `updated_at` 索引。

### 4.2 后续可扩展集合（按需）

- **projects / apps**：与 `task_id` 关联，存生成出的应用元数据、名称、路径等。
- **users**：若以后做多用户，可先预留。

## 五、实现步骤（推荐顺序）

1. **依赖与配置**
   - 在 `pyproject.toml` 增加：`motor`（或 `pymongo`）。
   - 在 `.env` 中增加 `MONGODB_URI`（及可选的 `MONGODB_DB_NAME`）。
   - 在 `backend/config.py` 中读取并导出，便于 `connection.py` 使用。

2. **连接层**
   - 实现 `backend/db/connection.py`：单例或依赖注入获取 `MotorClient`/`MongoClient`，提供 `get_database()`。
   - 在 `main.py` 的 `lifespan`（或 `on_event("startup")`/`on_event("shutdown")`）中：启动时建连、关闭时关闭连接。

3. **Repository 层**
   - 实现 `TaskRepository`：`create`, `get_by_id`, `update`, `list_all`, `list_ids`，文档字段与现有 `task_store.json` 结构一致。
   - 在 `create` 里生成 UUID 作为 `task_id`；`update` 支持部分更新（status、progress、append log、result）。

4. **接入 TaskManager**
   - 修改 `TaskManager`：构造函数接受一个 `TaskRepository`（或从 `db` 包获取默认实例）；`_load`/`_save` 改为调用 repository，不再读写 JSON 文件。
   - 保持对外接口不变，这样 `main.py` 和 `generator_service` 无需改 API 调用。

5. **可选优化**
   - 为 `tasks` 建唯一索引：`task_id`；按需建 `created_at`。
   - 若单机多 worker：当前设计已支持（多进程/多实例共享同一 MongoDB）。
   - 若需「从旧 JSON 迁移到 MongoDB」，可写一次性脚本：读 `task_store.json`，逐条 `insert_one` 到 `tasks`（注意去重或只迁移未在 DB 中的）。

6. **测试与回退**
   - 单元测试：Mock `TaskRepository` 或使用本地 MongoDB（如 Docker），覆盖 `create_task`、`update_task`、`get_task`、`get_all_tasks`。
   - 回退：保留一段时间的 JSON 落盘逻辑或双写，通过配置开关在「仅 JSON / 仅 MongoDB / 双写」之间切换，便于出问题时回退。

## 六、配置示例

**.env**

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=vibecoder
```

**backend/config.py（示例）**

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "vibecoder"
    class Config:
        env_file = ".env"

settings = Settings()
```

## 七、接口保持不变

以下接口保持与现在一致，仅数据源从 JSON 改为 MongoDB：

- `POST /api/generate` → 内部 `task_manager.create_task()` + 后台线程
- `GET /api/all_tasks_id` → `task_manager.retrieve_task_id()`
- `GET /api/all_tasks` → `task_manager.get_all_tasks()`
- `GET /api/tasks/{task_id}` → `task_manager.get_task(task_id)`
- `POST /api/refine` → 先 `task_manager.get_task()` 再启 refinement 线程

因此前端无需改动，只需保证后端启动时能连上 MongoDB（或通过配置回退到 JSON）。

## 八、小结

- 用 **Motor（异步）或 PyMongo（同步）** 连接 MongoDB，在 **config + connection + task_repository** 三层中完成接入。
- **TaskManager** 只做门面，真实持久化交给 **TaskRepository**，便于测试和以后换存储。
- 集合 **tasks** 与现有 JSON 结构对齐，便于迁移与双写回退。
- 先实现「任务」的 CRUD 与现有 API 对接，再按需扩展 projects/users 等集合。

按上述步骤即可在现有 FastAPI + TaskManager 架构下，平滑引入 MongoDB 作为后端数据库。
