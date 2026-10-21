"""最小测试：用云端 OpenAI 兼容接口做一次 chat 调用"""
import sys
import io

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from openai import OpenAI

client = OpenAI(
    api_key="sk-KU6R7I0Rre8vtSM3ypBfvLpR1ifrOSz4XOhZHX4CrHupF8ve",
    base_url="https://api.hcnsec.cn/v1",
)

print("开始 chat 调用...")
resp = client.chat.completions.create(
    model="auto",
    messages=[{"role": "user", "content": "你好，用一句话回复我：测试成功"}],
    timeout=60,
)
print("回复:", resp.choices[0].message.content)
