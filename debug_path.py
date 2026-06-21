import sys
import os

print(f"1. Python Executable: {sys.executable}")
print(f"2. CWD: {os.getcwd()}")
print("3. Attempting to find litellm in sys.modules...")

try:
    import litellm
    print(f"SUCCESS: {litellm.__file__}")
except ImportError as e:
    print(f"FAIL: {e}")
    
print("\n4. Current sys.path (Python looks for libraries here):")
for p in sys.path:
    print(p)