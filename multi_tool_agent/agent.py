"""
多功能智能助手 Agent（LangChain 1.x）
内置 5 个工具：
  1. get_weather   查询天气
  2. calculator    数学计算
  3. get_time      时间查询
  4. currency_convert 货币转换
  5. web_search   信息搜索
通过 .env 的 BACKEND 切换后端：openai 兼容接口 / 本地 ollama
"""
import os
import math
from datetime import datetime

import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent

# 从 .env 加载环境变量
load_dotenv()


# ============ 工具 1：查询天气 ============
@tool
def get_weather(city: str) -> str:
    """查询指定城市的当前天气（温度、天气状况、风力）。当用户问天气相关问题时使用。"""
    # 使用 wttr.in 的免费接口（无需 key），返回简洁中文信息
    try:
        resp = requests.get(
            f"https://wttr.in/{city}?format=3", timeout=10
        )
        if resp.status_code == 200 and resp.text.strip():
            return f"{city} 的天气：{resp.text.strip()}"
        return f"暂时无法获取 {city} 的天气信息。"
    except Exception as e:
        return f"查询 {city} 天气时出错：{e}"


# ============ 工具 2：数学计算 ============
@tool
def calculator(expression: str) -> str:
    """计算一个数学表达式，例如 "23 * 45 + (12 / 4) ** 2"。支持 + - * / ** () 等运算符。当用户需要算数、数学运算时使用。"""
    try:
        # 仅允许安全的数学符号，避免代码注入
        allowed = set("0123456789+-*/().% ")
        if not set(expression) <= allowed:
            return "表达式包含不允许的字符，仅支持数字与 + - * / ** ( ) % 运算。"
        # 提供常用数学函数
        safe_env = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        result = eval(expression, {"__builtins__": {}}, safe_env)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算失败，请检查表达式：{e}"


# ============ 工具 3：时间查询 ============
@tool
def get_time(timezone: str = "local") -> str:
    """查询当前时间。timezone 可选 'local'（本地时间）或 'utc'（世界标准时间）。当用户问现在几点、日期、时间时使用。"""
    now = datetime.now()
    if timezone.lower() == "utc":
        now = datetime.utcnow()
        return f"当前 UTC 时间：{now.strftime('%Y-%m-%d %H:%M:%S')}"
    return f"当前本地时间：{now.strftime('%Y-%m-%d %H:%M:%S')}（星期{['一','二','三','四','五','六','日'][now.weekday()]}）"


# ============ 工具 4：货币转换 ============
@tool
def currency_convert(amount: float, from_currency: str, to_currency: str) -> str:
    """把一定金额从一种货币转换为另一种货币。例如 amount=100, from_currency='USD', to_currency='CNY'。当用户问汇率、换钱、货币换算时使用。货币代码用大写，如 USD/CNY/EUR/JPY/GBP。"""
    try:
        # 使用 frankfurter.app 免费汇率接口（无需 key，基于 ECB 数据）
        url = (
            f"https://api.frankfurter.app/latest"
            f"?amount={amount}&from={from_currency.upper()}&to={to_currency.upper()}"
        )
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            rate = data.get("rates", {}).get(to_currency.upper())
            if rate is not None:
                return f"{amount} {from_currency.upper()} = {rate} {to_currency.upper()}（汇率更新时间：{data.get('date')}）"
        return f"无法获取 {from_currency} 到 {to_currency} 的汇率，请检查货币代码。"
    except Exception as e:
        return f"货币转换失败：{e}"


# ============ 工具 5：信息搜索 ============
@tool
def web_search(query: str) -> str:
    """在互联网上搜索信息并返回前几条结果摘要。当用户需要查找资料、新闻、百科、通用知识时使用。"""
    try:
        # 使用 DuckDuckGo 的 HTML 接口做轻量搜索
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers=headers,
            timeout=10,
        )
        if resp.status_code != 200:
            return f"搜索失败（状态码 {resp.status_code}）。"
        # 粗略提取结果标题与片段
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for item in soup.select(".result__body")[:5]:
            title = item.select_one(".result__a")
            snippet = item.select_one(".result__snippet")
            if title:
                results.append(
                    f"- {title.get_text(strip=True)}"
                    + (f"：{snippet.get_text(strip=True)}" if snippet else "")
                )
        if results:
            return "搜索结果：\n" + "\n".join(results)
        return "未找到相关结果。"
    except Exception as e:
        return f"搜索出错：{e}"


def build_agent():
    # 后端选择：openai（默认，兼容任意 OpenAI 风格接口）或 ollama（本地）
    backend = (os.getenv("BACKEND") or "openai").lower()

    if backend == "ollama":
        from langchain_ollama import ChatOllama

        llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL") or "qwen3:0.5b",
            base_url=os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434",
            temperature=0,
        )
    else:
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY") or ""
        if not api_key or api_key == "你的_api_key":
            raise RuntimeError(
                "请在 .env 填写真实的 OPENAI_API_KEY，"
                "并把 OPENAI_BASE_URL 指向你的模型服务（OpenAI / DeepSeek / 通义等）。"
            )
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo",
            temperature=0,
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL") or None,
        )

    tools = [
        get_weather,
        calculator,
        get_time,
        currency_convert,
        web_search,
    ]
    agent = create_agent(llm, tools)
    return agent
