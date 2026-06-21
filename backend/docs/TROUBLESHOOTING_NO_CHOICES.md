# 故障排查：API 返回 `choices: []`（无生成内容）

当流水线报错 **"model 'gemini/gemini-2.5-pro' returned no choices"** 且响应中 `completion_tokens: 0`、`prompt_tokens > 0` 时，表示请求已到达上游 API，但模型没有返回任何文本。

---

## 可能原因

| 原因 | 说明 | 建议 |
|------|------|------|
| **安全/策略拦截** | Gemini 对当前 prompt 或上下文（如 QA 报告、代码片段）触发了安全/策略过滤，直接不生成内容，返回空 `choices`。 | 检查本轮 QA 报告与代码中是否含敏感词或易误判内容；换一种表述或略去无关片段再试。 |
| **限流 / 配额** | 请求被限流或配额用尽，部分实现会返回 200 + 空 `choices` 而非 429。 | 查看 Google AI / Vertex 控制台用量与配额；稍后重试或升级配额。 |
| **模型/区域不可用** | `gemini-2.5-pro` 在你使用的区域或账号下不可用、或路由错误（如 LiteLLM 的 `gemini/` 前缀指向的端点不对）。 | 确认该模型在你的 API 密钥对应项目中可用；尝试改用 `gemini-2.5-flash` 或其它可用模型。 |
| **上游瞬时故障** | API 端临时异常，返回了空内容。 | 重试 1～2 次；若持续出现则换时间段或换模型。 |
| **输出被截断或过滤** | 极少数情况下输出因长度/策略被完全丢弃，表现为空 `choices`。 | 缩短 prompt 或拆步；或换模型验证。 |

---

## 应对步骤

1. **先重试**  
   同一任务多跑一次，排除瞬时故障。

2. **用 Flash 做验证**  
   在 `generator_service.py` 中临时把 Auto Fix 使用的模型改为 `gemini_flash_model`（或通过下面环境变量），看是否仍出现空 `choices`。若 Flash 正常而 Pro 经常空，多半是 Pro 的配额/区域/策略问题。

3. **通过环境变量切换模型（若已实现）**  
   若项目支持 `VIBECODER_GEMINI_MODEL` 或类似变量，可设为 `gemini/gemini-2.5-flash` 再跑流水线。

4. **看上游返回的完整响应**  
   若响应里有 `vertex_ai_safety_results` 或类似字段且非空，说明被安全/策略拦截，需调整输入或联系 API 提供方。

5. **在服务层加“空 choices”重试**  
   在调用 `auto_fix_agent.run()` 处捕获 `AgentGenerationError`，若错误信息包含 `returned no choices`，则自动重试 1 次（同一模型或备用模型），再失败再报错并记录日志。

---

## 代码侧可选改动

- **备用模型**：Auto Fix 阶段使用 `gemini_pro_model`；可增加逻辑：当检测到 `no choices` 时，用 `gemini_flash_model` 再跑一次。
- **重试**：对 `agent.run()` 包一层重试（例如最多 2 次），仅在出现 `no choices` 或明确可重试的 API 错误时重试，避免无限重试。

---

*出现该错误时，优先重试 + 换 Flash 验证；若仍复现，再查配额、区域与安全策略。*
