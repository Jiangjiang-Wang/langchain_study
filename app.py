"""
最简单的 LangChain Agent 工程入口
运行: python app.py
"""
from langchain_core.messages import HumanMessage
from agent import build_agent


def main():
    # 1. 创建 agent（包含 LLM + 工具 + 推理循环）
    agent = build_agent()

    # 2. 直接提问（单轮对话）
    question = "你好，请用一句话介绍一下你自己。另外，北京今天天气怎么样？"
    print("用户:", question)

    result = agent.invoke({"messages": [HumanMessage(content=question)]})
    # result["messages"] 是完整消息列表，最后一条是 agent 的回复
    print("Agent:", result["messages"][-1].content)


if __name__ == "__main__":
    main()
    
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气。当你需要回答天气相关的问题时，使用此工具。"""
    # 这里用假数据演示，实际可对接天气 API
    return f"{city} 今天晴，25 摄氏度，微风。"

@tool
def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """获取当前时间
    Args: 
        timezone: 时区，默认为 Asia/Shanghai
    Returns:
        当前时间，格式为 %Y-%m-%d %H:%M:%S
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")