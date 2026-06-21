# 测试 Human Feedback Loop（/api/refine）

用**已生成好的 app** 测试 refine 时，只需：拿到该任务对应的 `task_id` → 调用 `POST /api/refine` → 轮询 `GET /api/tasks/{task_id}` 直到完成。

---

## 1. 前提

- 后端已启动（例如 `uv run python backend/main.py` 或 `uvicorn backend.main:app --reload`），默认端口 **8000**。
- 已有一次生成完成的任务，即存在目录：`generated_app/<task_id>/`，且其中有 `ui/`、PRD 等。

---

## 2. 获取可用的 task_id

任选一种方式。

**方式 A：查所有任务 ID**

```bash
curl -s http://127.0.0.1:8000/api/all_tasks_id
```

返回示例：

```json
{
  "status": "success",
  "task_ids": ["abc12345-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "def67890-..."]
}
```

任选一个 `task_id`（对应目录 `generated_app/<该 task_id>/` 存在且里面有 app 即可）。

**方式 B：查所有任务详情（含 status）**

```bash
curl -s http://127.0.0.1:8000/api/all_tasks
```

在返回的 `tasks` 里找 `status` 为 `"completed"` 的任务，用其 `task_id`。

**方式 C：你已知 task_id**

若你是用 `/api/generate` 生成过，或直接在文件系统里看到 `generated_app/` 下某个文件夹名，该文件夹名就是 `task_id`。

---

## 3. 调用 POST /api/refine

请求体为 JSON：`task_id` + `feedback`（必填）。

**curl 示例（请把 `YOUR_TASK_ID` 换成真实 task_id）：**

```bash
curl -X POST http://127.0.0.1:8000/api/refine \
  -H "Content-Type: application/json" \
  -d "{\"task_id\": \"YOUR_TASK_ID\", \"feedback\": \"Add a dark mode toggle button in the header.\"}"
```

成功时返回示例：

```json
{
  "status": "success",
  "message": "Refinement task started",
  "task_id": "YOUR_TASK_ID"
}
```

常见错误返回：

- `"Task not found"`：该 `task_id` 在系统里不存在。
- `"feedback is required"`：未传或 `feedback` 为空。
- `"Task is still running; wait for it to complete before refining"`：该任务仍在生成中，需等其 `status` 变为 `completed` 后再 refine。

---

## 4. 轮询任务状态

Refine 在后台执行，需轮询同一 `task_id` 的 task 状态。

**单次查询：**

```bash
curl -s http://127.0.0.1:8000/api/tasks/YOUR_TASK_ID
```

返回示例：

```json
{
  "status": "success",
  "task": {
    "status": "running",
    "progress": 0,
    "logs": ["...", "🔄 Refinement started. User feedback: ..."],
    "result": null
  }
}
```

- **status**：`"running"` 表示 refine 进行中；`"completed"` 表示完成；`"failed"` 表示失败。
- **logs**：会追加 refine 相关日志。
- **result**：完成后会有 `app_name`、`path`（应用路径）。

**简单轮询（每 5 秒查一次，直到完成）：**

```bash
# Linux/macOS (bash)
TASK_ID="YOUR_TASK_ID"
while true; do
  R=$(curl -s "http://127.0.0.1:8000/api/tasks/$TASK_ID")
  echo "$R" | head -c 500
  echo ""
  if echo "$R" | grep -q '"status":"completed"'; then echo "Done."; break; fi
  if echo "$R" | grep -q '"status":"failed"'; then echo "Failed."; break; fi
  sleep 5
done
```

Windows PowerShell 示例：

```powershell
$taskId = "YOUR_TASK_ID"
do {
  $r = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/tasks/$taskId"
  $r.task | ConvertTo-Json -Depth 5
  if ($r.task.status -eq "completed") { Write-Host "Done."; break }
  if ($r.task.status -eq "failed") { Write-Host "Failed."; break }
  Start-Sleep -Seconds 5
} while ($true)
```

---

## 5. 一键测试流程示例

假设后端在 `http://127.0.0.1:8000`：

```bash
# 1. 取一个已存在的 task_id（这里用列表第一个）
TASK_ID=$(curl -s http://127.0.0.1:8000/api/all_tasks_id | python -c "import sys,json; d=json.load(sys.stdin); print(d['task_ids'][0] if d.get('task_ids') else '')")

# 2. 发起 refine
curl -X POST http://127.0.0.1:8000/api/refine \
  -H "Content-Type: application/json" \
  -d "{\"task_id\": \"$TASK_ID\", \"feedback\": \"Change the main heading to 'My App' and add a footer with copyright.\"}"

# 3. 轮询（按需调整循环次数或间隔）
curl -s "http://127.0.0.1:8000/api/tasks/$TASK_ID" | python -m json.tool
```

完成后，到 `generated_app/<task_id>/ui/` 下查看或直接打开 `index.html` 验证修改是否符合你的 feedback。

---

## 6. 小结

| 步骤 | 方法 | 说明 |
|------|------|------|
| 获取 task_id | `GET /api/all_tasks_id` 或 `GET /api/all_tasks` | 选一个已完成的任务的 ID |
| 提交反馈 | `POST /api/refine`，Body: `{"task_id":"...", "feedback":"..."}` | 必填字段：task_id, feedback |
| 查看进度/结果 | `GET /api/tasks/{task_id}` | 看 `task.status`（running/completed/failed）和 `task.result` |

用已生成好的 app 测试 human feedback loop，就是：**用其 task_id 调一次 refine，再轮询 task 直到 completed，然后到对应目录看 app 是否按 feedback 被修改。**
