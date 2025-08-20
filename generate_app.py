import os
from am_tools import read_file, write_file, mkdir, list_files
from smolagents import CodeAgent, WebSearchTool # InferenceClientModel
from smolagents.models import OpenAIServerModel
from prompts.prompt_manager import PromptManager

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# 主函数：渲染提示词并运行 CodeAgent
def main():
    # Initialize the prompt manager
    prompt_manager = PromptManager()  # 初始化提示词管理器，用于渲染模板

    # Example usage with template variables
    app_name = "my_awesome_app"  # 应用名称示例
    app_description = "A modern React application for task management"  # 应用描述示例
    additional_requirements = [  # 额外需求列表
        "Use functional React components",
        "Implement responsive design",
        "Include dark/light theme toggle"
    ]
    tech_stack = "React 19, Vite, Shadcn UI, Tailwind CSS"  # 技术栈说明

    # Generate the prompt using Jinja2 templates
    prompt = prompt_manager.render_main_prompt(  # 使用模板渲染出完整的提示词
        app_name=app_name,
        app_description=app_description,
        additional_requirements=additional_requirements,
        tech_stack=tech_stack,
        feature_name="TaskManager"
    )

    # model = InferenceClientModel()  # 初始化推理模型客户端
    agent = CodeAgent(  # 初始化智能体，配置工具和模型
        tools=[read_file, write_file, list_files, mkdir], # WebSearchTool()
        model=OpenAIServerModel("gpt-5"),
        stream_outputs=False,  # 关闭流式
        additional_authorized_imports=["subprocess"],
    )

    agent.run(prompt)  # 执行提示词，触发应用生成流程

    # https://huggingface.co/docs/smolagents/v1.21.0/en/guided_tour#codeagent
    # TestAgent = CodeAgent() # Confirms the code is working (run tests / linter / open it in a headless browser)  # 初始化智能体，配置工具和模型


if __name__ == "__main__":
    main()