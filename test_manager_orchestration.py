import os
from pathlib import Path
from dotenv import load_dotenv
from vibecoder_engine import VibeCoderEngine  # type: ignore

try:
    from am_tools import agent_state  # type: ignore
except ImportError:
    # 兼容从包内运行的情况
    from VibeCoder.am_tools import agent_state  # type: ignore


# 确保可以从当前工程导入模块
CURRENT_DIR = Path(__file__).resolve().parent
os.chdir(CURRENT_DIR)

load_dotenv()


DEFAULT_TODO_REQUIREMENTS = """
    I want a generate a simple todo app named "ChaoChow2 todo" with basic features.
    """.strip()


def main() -> None:
    # 直接使用内置的 ToDo 应用需求
    user_requirements = DEFAULT_TODO_REQUIREMENTS

    print("=== 线性 Pipeline App 生成测试 ===")
    print("用户需求如下：")
    print("-" * 40)
    print(user_requirements)
    print("-" * 40)

    engine = VibeCoderEngine()

    # 使用原有线性 sequential pipeline（非 manager 编排）
    success = engine.generate_app(user_requirements=user_requirements, use_manager=False)

    if not success:
        print("❌ 线性 Pipeline 生成失败，请检查上方日志输出。")
        raise SystemExit(1)

    app_name = agent_state.get_app_name()
    app_path = agent_state.get_app_folder_path()

    print("✅ 线性 Pipeline 生成完成！")
    print(f"应用名称: {app_name}")
    print(f"应用路径: {app_path}")
    print()
    print("你可以直接用浏览器打开生成目录下的 `ui/index.html` 来体验效果。")


if __name__ == "__main__":
    main()

