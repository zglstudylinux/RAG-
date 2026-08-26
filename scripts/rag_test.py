"""Run a set of manual RAG test cases against the live knowledge base.

Usage:
    python scripts/rag_test.py              # run the built-in cases
    python scripts/rag_test.py "你的问题"     # ask a single custom question

Results are printed to stdout and appended to docs/rag_test_results.md.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

TEST_CASES: list[tuple[str, str]] = [
    ("芯片规格", "AB5766C 的 CPU 是什么架构，主频多少？"),
    ("芯片规格", "AB5766C 的 Flash 和 RAM 容量分别是多少？"),
    ("芯片规格", "AB5766C 的 2.4G 射频最大发射功率和接收灵敏度是多少？"),
    ("芯片规格", "AB5766C 的供电电压范围、封装尺寸和工作温度？"),
    ("外设", "AB5766C 有哪些 UART 串口？"),
    ("外设", "AB5766C 的 SAR ADC 分辨率是多少？有几个？触摸按键有几个？"),
    ("驱动API", "如何初始化 AB5766C 的 GPIO？用哪个函数和结构体？"),
    ("驱动API", "GPIO 的 CrossBar 功能映射用什么函数配置？"),
    ("驱动API", "GPIO 上拉/下拉电阻有哪些可选阻值？"),
    ("BSP", "BSP 层包含哪些模块？"),
    ("音频", "SDK 里支持哪些音频解码格式？"),
    ("无线", "无线麦克风 wireless mic 相关的处理模块有哪些？"),
    ("原理图", "领夹MIC 接收端(Receiver)原理图包含哪些主要器件和接口？"),
    ("开发指南", "AB5766X SDK 主要支持哪两种产品？"),
    ("开发指南", "AB5766X SDK 使用什么操作系统？"),
    ("开发指南", "编译环境需要哪些工具和版本？"),
    ("开发指南", "SDK 的 modules 目录下有哪些子模块？"),
    ("开发指南", "SDK 支持的音频编解码格式是什么？"),
]


async def _run(questions: list[tuple[str, str]]) -> None:
    from ragkb.config import get_settings
    from ragkb.core.factory import build_services

    settings = get_settings()
    services = build_services(settings)
    lines: list[str] = []
    try:
        for category, question in questions:
            answer = await services.rag.answer(question, k=settings.retrieval_top_k)
            block = [f"### [{category}] {question}", ""]
            block.append((answer.text or "").strip())
            block.append("")
            block.append("**引用来源：**")
            for i, citation in enumerate(answer.citations, start=1):
                page = f" p.{citation.page}" if citation.page else ""
                block.append(f"- [{i}] `{citation.source}`{page}")
            block.append("")
            text = "\n".join(block)
            print(text)
            lines.append(text)
    finally:
        services.store.close()

    out = Path("docs/rag_test_results.md")
    header = "# RAG 真实检索测试结果\n\n> 自动生成，模型：deepseek-v4-pro-0813 + 本地 BGE。\n\n"
    out.write_text(header + "\n".join(lines), encoding="utf-8")
    print(f"\n[已保存到 {out}]")


def main() -> int:
    if len(sys.argv) > 1:
        questions = [("自定义", " ".join(sys.argv[1:]))]
    else:
        questions = TEST_CASES
    asyncio.run(_run(questions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
