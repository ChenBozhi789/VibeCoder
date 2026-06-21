import os
from smolagents import CodeAgent, ToolCallingAgent, DuckDuckGoSearchTool
from backend.utils.normalized_litellm_model import NormalizedLiteLLMModel
import litellm

# 使用 LiteLLMModel 连接 Gemini API
# 也可以换成 HfApiModel 或 OpenAIServerModel 连接其他模型
model = NormalizedLiteLLMModel(
    model_id="gemini/gemini-3.1-pro-preview",
    api_key=os.environ.get("GEMINI_API_KEY"),
    max_retries=3,
)

# ------------------------------------------------------------------
# 角色 A: 文档研究员 (Worker Agent)
# ------------------------------------------------------------------
# 它的特点是使用 ToolCallingAgent，适合按部就班地调用搜索工具
research_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool()], # 给它配备搜索引擎
    model=model,
    name="docs_researcher", # 【关键】Manager 通过这个名字来呼叫它
    description="Searches the web for library documentation and latest API usage examples."
)

# ------------------------------------------------------------------
# 角色 B: 技术主管 (Manager Agent)
# ------------------------------------------------------------------
# 它的特点是 CodeAgent，它会写 Python 代码来解决问题，并能管理其他 Agent
manager_agent = CodeAgent(
    tools=[], 
    model=model,
    # 【关键】在这里我们将 research_agent 注册为它的下属
    managed_agents=[research_agent], 
    # 允许 Agent 在生成的代码中导入这些库（沙盒安全限制）
    additional_authorized_imports=["pandas", "json", "datetime"] 
)

# ------------------------------------------------------------------
# 运行任务
# ------------------------------------------------------------------
# 这是一个简单的演示任务：Manager 需要查找信息，然后编写代码
task = """
1. Ask the researcher to find out what is the current year.
2. Based on that information, write a simple Python script that calculates how many years have passed since the year 2000.
"""

print("User Task:", task)
result = manager_agent.run(task)

print("\nFinal Output:\n", result)