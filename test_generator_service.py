"""
测试 generator_service.py 的独立脚本。

用法（在项目根目录执行）:
    python test_generator_service.py

或指定自定义需求:
    python test_generator_service.py "I want a simple todo app"
"""
import os
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
CURRENT_DIR = Path(__file__).resolve().parent
os.chdir(CURRENT_DIR)
sys.path.insert(0, str(CURRENT_DIR))

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 导入需在 sys.path 配置后执行
from backend.utils.task_manager import task_manager, TaskStatus
from backend.services.generator_service import run_app_generation_task


DEFAULT_REQUIREMENTS = """
I want to generate a simple Minesweeper game named "Super Mine Sweeper" with basic features.
""".strip()


def main() -> None:
    user_requirements = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REQUIREMENTS

    print("=== generator_service 测试 ===")
    print("用户需求:")
    print("-" * 40)
    print(user_requirements)
    print("-" * 40)

    # 1. 创建任务
    task_id = task_manager.create_task()
    print(f"\n任务已创建: {task_id}\n")

    # 2. 同步执行生成（会阻塞，Agent 输出会直接打印到控制台）
    try:
        run_app_generation_task(task_id=task_id, user_requirements=user_requirements)
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        raise SystemExit(1)

    # 3. 获取任务结果
    task = task_manager.get_task(task_id)
    if not task:
        print("\n❌ 任务不存在")
        raise SystemExit(1)

    print("\n" + "=" * 50)
    print("任务状态:", task.get("status"))
    print("进度:", task.get("progress"), "%")
    print("\n日志摘要:")
    for log in task.get("logs", [])[-10:]:  # 只显示最后 10 条
        print(f"  - {log}")

    result = task.get("result")
    if result:
        print("\n✅ 生成完成!")
        print(f"  应用名称: {result.get('app_name', 'N/A')}")
        print(f"  输出路径: {result.get('path', 'N/A')}")
    else:
        print("\n⚠️ 任务完成但无 result 字段，请检查上方日志")


if __name__ == "__main__":
    main()
