from markdown_it import MarkdownIt
from config import llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import SimpleJsonOutputParser
from langchain_core.output_parsers import StrOutputParser
import json
from enum import Enum


class DataMode(Enum):
    ALPACA = (1,)
    MD = 2


class ChatMode(Enum):
    CHAT_QA = (1,)
    CHAT_QA_EXT = (2,)
    CHAT_MD = 3


DATA_MODE = DataMode.ALPACA
CHAT_MODE = ChatMode.CHAT_MD
HAS_ALPACA_DATA = False


def convert(from_file, to_file):
    global HAS_ALPACA_DATA
    if DATA_MODE == DataMode.ALPACA:
        HAS_ALPACA_DATA = False
        with open(to_file, "a", encoding="utf-8") as file:
            file.write("[")

    md = MarkdownIt()
    with open(from_file, "r", encoding="utf-8") as f:
        markdown_text = f.read()
    tokens = md.parse(markdown_text)
    titles = []
    contents = []
    flag = False
    for index, token in enumerate(tokens):
        if flag and (token.type == "heading_open"):
            write_to_file(titles, contents, to_file)
            keep_level = int(token.tag[1]) - 1
            titles = titles[:keep_level]
            contents.clear()
            flag = False

        if token.type == "heading_open":
            titles.append(tokens[index + 1].content)

        if token.type == "html_block":
            if not flag:
                flag = True
            contents.append(token.content.strip())

        if token.type == "paragraph_open":
            if not flag:
                flag = True
            contents.append(tokens[index + 1].content)

        if index == (len(tokens) - 1) and token.type != "heading_close":
            write_to_file(titles, contents, to_file)

    if DATA_MODE == DataMode.ALPACA:
        with open(to_file, "a", encoding="utf-8") as file:
            file.write("]")


def write_to_file(titles, contents, to_file):
    if DATA_MODE == DataMode.ALPACA:
        write_to_alpaca(titles, contents, to_file)
    if DATA_MODE == DataMode.MD:
        write_to_md(titles, contents, to_file)


def write_to_md(titles, contents, to_file):
    with open(to_file, "a", encoding="utf-8") as file:
        file.write("# " + "-".join(titles) + "\n")
        file.write("\n".join(contents).strip() + "\n" + "\n")


def write_to_alpaca(titles, contents, to_file):
    global CHAT_MODE
    global HAS_ALPACA_DATA
    alpaca_list = []

    success = False
    while not success:
        try:
            if CHAT_MODE == ChatMode.CHAT_QA:
                alpaca_list = chat("-".join(titles), "\n".join(contents).strip())

            if CHAT_MODE == ChatMode.CHAT_QA_EXT:
                alpaca_list = chat_ext("-".join(titles), "\n".join(contents).strip())

            if CHAT_MODE == ChatMode.CHAT_MD:
                alpaca_list = chat_md("-".join(titles), "\n".join(contents).strip())

            success = True
        except Exception as e:
            print(f"捕获到异常: {e}")

    with open(to_file, "a", encoding="utf-8") as file:
        for alpaca in alpaca_list:
            if HAS_ALPACA_DATA:
                file.write(",")
            file.write(json.dumps(alpaca, ensure_ascii=False))
            HAS_ALPACA_DATA = True


def chat(title: str, content: str):
    print("Q1: " + title)

    system_template = """
    我有一对问答，希望你帮我修改提问但又不能偏离原提问的本意，使修改后的提问跟答案匹配，不要修改答案，修改后的提问不要有章节信息

    要求：
    1. 格式：
    ```json
    {{
    "instruction": "", //优化后的提问
    }}
    ```

    提问：
    {title}

    答案：
    {content}
    """
    prompt_template = ChatPromptTemplate.from_messages([("system", system_template)])
    chain = prompt_template | llm | SimpleJsonOutputParser()
    result = chain.invoke({"title": title, "content": content})
    result["input"] = ""
    result["output"] = content

    print("Q2: " + result["instruction"])
    print("")
    return [result]


def evaluation_alpaca(instruction: str, output: str):
    system_template = """
    请仔细分析以下 Alpaca 数据集样本,并根据给定标准对其质量进行评估:

    指令: {instruction}
    输出: {output}

    评估标准:

    1. 指令清晰度 (1-10分): 指令是否明确、易于理解?

    2. 输出相关性 (1-10分): 输出是否与指令直接相关?

    3. 输出质量 (1-10分): 输出是否准确、全面且适当地回应了指令?

    4. 语言质量 (1-10分): 指令和输出的语言是否流畅、语法正确、表达清晰?

    5. 伦理性 (通过/不通过): 指令和输出的内容是否不包含偏见、歧视或不当信息?

    总体评价 (1-10分): 

    改进建议:

    请根据以上标准进行评估,为每项给出评分和简要解释。然后,给出总体评价和具体的改进建议。
    """
    prompt_template = ChatPromptTemplate.from_messages([("system", system_template)])
    chain = prompt_template | llm | StrOutputParser()
    result = chain.invoke({"instruction": instruction, "output": output})

    print(result)
    print("")


def chat_ext(title: str, content: str):
    print("Q1: " + title)

    system_template = """
    您的任务是将我提供的 Markdown 格式文本片段转换成问答对的形式，并以指定的 JSON 格式输出。文本片段的标题结构为"章-节-小节"。请严格遵循以下指南：

    1. 仔细阅读提供的 Markdown 文本内容，包括章节标题和正文。
    2. 识别内容中的关键信息和主要观点。
    3. 为每个关键点创建一个相关的问题。
    4. 提供准确、简洁的答案，直接基于原文内容。
    5. 确保问题和答案是连贯的，并涵盖原文的主要内容。
    6. 使用清晰、直接的中文语言。

    额外要求：
    7. 不要在问题中直接引用章节编号或标题。将重点放在内容上，而不是结构上。
    8. 如果答案中包含列表，请从1开始编号，不要使用原文的编号。
    9. 确保每个问题都是完整且独立的。即使脱离上下文，读者也能理解问题的含义。
    10. 所有问答对必须使用中文。
    11. 问题应该反映章节的主题，但不要直接引用"第X章"、"第X节"等字样。
    12. 不要在问题中引用上下文。

    输出格式：
    请将生成的问答对按以下 JSON 数组格式输出：

    [
    {{
        "instruction": "问题内容",
        "input": "",
        "output": "答案内容"
    }},
    {{
        "instruction": "问题内容",
        "input": "",
        "output": "答案内容"
    }}
    ]

    注意：
    - "instruction" 字段包含问题。
    - "input" 字段始终为空字符串。
    - "output" 字段包含答案。
    - 确保 JSON 格式正确，可以被有效解析。

    请开始转换以下 Markdown 格式的内容为符合要求的中文问答对，并以指定的 JSON 格式输出：

    {content}
    """
    prompt_template = ChatPromptTemplate.from_messages([("system", system_template)])
    chain = prompt_template | llm | SimpleJsonOutputParser()
    result = chain.invoke({"content": "# " + title + "\n" + content})

    print("")
    return result


def chat_md(title: str, content: str):
    alpaca_data = {"instruction": "# " + title, "input": "", "output": content}
    return [alpaca_data]


if __name__ == "__main__":
    # convert('序.md', '序-RESULT.json')
    # convert('第一章.md', '第一章-RESULT.json')
    # convert('第二章.md', '第二章-RESULT.json')
    # convert('第三章.md', '第三章-RESULT.json')
    # convert('第四章.md', '第四章-RESULT.json')
    # convert('第五章.md', '第五章-RESULT.json')
    # convert('第六章.md', '第六章-RESULT.json')
    # convert('尾.md', '尾-RESULT.json')

    convert(
        "MD文件.md",
        "MD文件-RESULT.json",
    )
