"""测试云端 OpenAI 兼容接口的 API 密钥是否有效"""
import sys
import io

# Windows 控制台默认 GBK，无法打印 ❌/⚠️ 等 emoji，强制 UTF-8
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from openai import OpenAI
from openai import APIError, AuthenticationError, RateLimitError

api_key = "sk-KU6R7I0Rre8vtSM3ypBfvLpR1ifrOSz4XOhZHX4CrHupF8ve"
base_url = "https://api.hcnsec.cn/v1"

client = OpenAI(api_key=api_key, base_url=base_url)


def test_api_key():
    print("正在测试 API 密钥...")
    try:
        models = client.models.list()
        first_model = models.data[0].id if models.data else "未知模型"
        print("✅ 密钥有效！连接成功。")
        print(f"  可用模型示例: {first_model}")
    except AuthenticationError as e:
        print("❌ 验证失败：API 密钥无效或已过期。")
        print(f"  错误详情: {e}")
    except RateLimitError:
        print("⚠️ 连接成功，但触发了速率限制。密钥本身是有效的。")
    except APIError as e:
        print(f"❌ API 错误：{e.status_code} - {e.message}")
    except Exception as e:
        print(f"❌ 发生未知错误：{e}")


if __name__ == "__main__":
    test_api_key()
