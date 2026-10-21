"""
多功能智能助手 - 运行入口
功能：天气查询 / 数学计算 / 时间查询 / 货币转换 / 信息搜索
"""
import sys
import io

# Windows 控制台默认 GBK，无法打印 emoji（如 ☀），强制 stdout/stderr 用 UTF-8
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from langchain_core.messages import HumanMessage

from agent import build_agent


def main():
    agent = build_agent()

    # 你可以自由修改下面的问题，测试不同工具
    questions = [
        "北京今天天气怎么样？",
        "帮我算一下 (128 * 45 + 300) / 6 等于多少？",
        "现在几点了？",
        "100 美元能换多少人民币？",
        "搜索一下 LangChain 是什么。",
    ]

    for q in questions:
        print(f"\n用户: {q}")
        result = agent.invoke({"messages": [HumanMessage(content=q)]})
        # 取最后一条 AI 消息作为回复
        answer = result["messages"][-1].content
        print(f"助手: {answer}")


if __name__ == "__main__":
    main()
