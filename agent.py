"""
最简单的 LangChain Agent 构建模块（LangChain 1.x）
支持两种后端，通过 .env 的 BACKEND 切换：
  - openai  : 任意 OpenAI 兼容接口（OpenAI / DeepSeek / 通义 / 智谱 / 公司内部网关等）
  - ollama  : 本地 Ollama 服务（需先 ollama pull 模型）

说明：本项目运行环境无法直连 Ollama 官方模型仓库，且本地无可用 GPU/torch 推理，
因此默认推荐用 openai 兼容接口（国内服务可直连）。
"""
import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

# 从 .env 加载环境变量
load_dotenv()


@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气。当你需要回答天气相关的问题时，使用此工具。"""
    # 这里用假数据演示，实际可对接天气 API
    return f"{city} 今天晴，25 摄氏度，微风。"


def build_agent():
    # 后端选择：openai（默认）或 ollama
    backend = (os.getenv("BACKEND") or "openai").lower()

    if backend == "ollama":
        from langchain_ollama import ChatOllama

        llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL") or "qwen3:0.5b",
            base_url=os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434",
            temperature=0,
        )
    else:
        # 默认走 OpenAI 兼容接口：把 base_url 指向任何兼容服务即可
        api_key = os.getenv("OPENAI_API_KEY") or ""
        if not api_key or api_key == "你的_api_key":
            raise RuntimeError(
                "请在 .env 填写真实的 OPENAI_API_KEY，"
                "并把 OPENAI_BASE_URL 指向你的模型服务地址（OpenAI / DeepSeek / 通义等）。"
            )
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo",
            temperature=0,
            api_key=api_key,
            # base_url 为空时不传，走 OpenAI 官方；填了就走兼容服务
            base_url=os.getenv("OPENAI_BASE_URL") or None,
            str
        )

    # 注册工具并构建 agent（create_agent 自带 ReAct 推理循环）
    tools = [get_weather]
    agent = create_agent(llm, tools)
    return agent