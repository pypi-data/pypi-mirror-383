"""
Example: Using environment variables for configuration
"""

import os
from xiaoshiai_hub import hf_hub_download, snapshot_download, DEFAULT_BASE_URL

print("=" * 80)
print("示例：使用环境变量配置")
print("=" * 80)
print()

# 1. 查看当前配置
print("1. 查看当前 Hub URL 配置")
print("-" * 80)
print(f"DEFAULT_BASE_URL: {DEFAULT_BASE_URL}")
print(f"环境变量 MOHA_ENDPOINT: {os.environ.get('MOHA_ENDPOINT', '未设置')}")
print()

# 2. 方法 1: 使用默认配置（从环境变量读取）
print("2. 方法 1: 使用默认配置")
print("-" * 80)
print("不指定 base_url，SDK 会自动使用环境变量或默认值")
print()

# 配置
REPO_ID = "demo/demo"
USERNAME = "4508b2b0-af7c-4dcf-9b91-bf84421f043c"
PASSWORD = "3498977a-ddc5-4501-9719-0302986ff464"

# 下载文件（使用环境变量配置）
print(f"下载文件，使用 URL: {DEFAULT_BASE_URL}")
try:
    file_path = hf_hub_download(
        repo_id=REPO_ID,
        filename="Dockerfile",
        # 不指定 base_url，使用环境变量或默认值
        username=USERNAME,
        password=PASSWORD,
    )
    print(f"✓ 文件已下载到: {file_path}")
except Exception as e:
    print(f"✗ 下载失败: {e}")

print()

# 3. 方法 2: 在代码中动态设置环境变量
print("3. 方法 2: 在代码中动态设置环境变量")
print("-" * 80)
print("在导入 SDK 之前设置环境变量")
print()

# 注意：这个示例仅用于演示
# 实际使用中，应该在导入 SDK 之前设置环境变量
# 这里因为已经导入了，所以不会生效

# 示例代码（需要在新的 Python 进程中运行）:
print("示例代码：")
print("""
import os

# 在导入 SDK 之前设置
os.environ['MOHA_ENDPOINT'] = 'https://custom-url.com/api/moha'

# 然后导入 SDK
from xiaoshiai_hub import hf_hub_download

# 现在会使用自定义的 URL
file_path = hf_hub_download(...)
""")
print()

# 4. 方法 3: 显式指定 URL（优先级最高）
print("4. 方法 3: 显式指定 URL（优先级最高）")
print("-" * 80)
print("显式指定 base_url 参数会覆盖环境变量")
print()

# 使用显式指定的 URL
custom_url = "https://rune.develop.xiaoshiai.cn/api/moha"
print(f"使用自定义 URL: {custom_url}")

try:
    file_path = hf_hub_download(
        repo_id=REPO_ID,
        filename="Dockerfile",
        base_url=custom_url,  # 显式指定
        username=USERNAME,
        password=PASSWORD,
    )
    print(f"✓ 文件已下载到: {file_path}")
except Exception as e:
    print(f"✗ 下载失败: {e}")

print()

# 5. 实际使用建议
print("5. 实际使用建议")
print("-" * 80)
print("""
推荐做法：

1. 开发环境：
   export MOHA_ENDPOINT="https://dev.xiaoshiai.cn/api/moha"

2. 测试环境：
   export MOHA_ENDPOINT="https://test.xiaoshiai.cn/api/moha"

3. 生产环境：
   export MOHA_ENDPOINT="https://hub.xiaoshiai.cn/api/moha"

4. 在代码中：
   # 不指定 base_url，让 SDK 自动使用环境变量
   file_path = hf_hub_download(
       repo_id="demo/demo",
       filename="config.yaml",
       username="user",
       password="pass",
   )

这样可以在不同环境中使用相同的代码，只需要设置不同的环境变量即可。
""")

print()
print("=" * 80)
print("更多信息请查看: ENVIRONMENT_VARIABLES.md")
print("=" * 80)

