#!/usr/bin/env python3
"""
测试fetch功能 - 测试wttr.in天气API
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_server_fetch.server import fetch_url


async def test_wttr_fetch():
    """测试wttr.in天气API抓取"""
    print("=== 测试: wttr.in 天气API ===")
    url = "https://wttr.in/Shanghai?format=j1"
    print(f"正在抓取: {url}")

    start_time = time.time()
    try:
        content, prefix = await fetch_url(url, "Mozilla/5.0", False, None)
        end_time = time.time()
        print(f"✅ 抓取成功！耗时: {end_time - start_time:.2f}秒")
        print(f"内容长度: {len(content)} 字符")
        print(f"内容预览: {content[:200]}...")

        # 尝试解析JSON内容
        import json

        try:
            data = json.loads(content)
            print(f"✅ JSON解析成功！")
            if "current_condition" in data:
                current = data["current_condition"][0]
                print(f"当前温度: {current.get('temp_C', 'N/A')}°C")
                print(
                    f"天气状况: {current.get('weatherDesc', [{}])[0].get('value', 'N/A')}"
                )
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析失败: {e}")

    except Exception as e:
        end_time = time.time()
        print(f"❌ 抓取失败: {e}")
        print(f"耗时: {end_time - start_time:.2f}秒")


async def main():
    """运行测试"""
    print("开始测试 wttr.in 天气API...")
    await test_wttr_fetch()
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
