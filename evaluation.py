import json
import random
from langchain_core.prompts import ChatPromptTemplate
from config import llm
from langchain_core.output_parsers import StrOutputParser
import requests
from logger import Logger

logger = Logger('app.log')


def random_copy_qa(file_path: str, count: int):
    with open(file_path, 'r', encoding='utf-8') as file:
        json_array = json.load(file)
        return random.sample(json_array, count)


def write_json_array_to_file(json_array, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_array, file, ensure_ascii=False, indent=4)


def generate_random_qa():
    array = []
    array.extend(random_copy_qa("存档/QA-EXT/序-Alpaca-Ext.json", 3))
    array.extend(random_copy_qa("存档/QA-EXT/第一章-Alpaca-Ext.json", 10))
    array.extend(random_copy_qa("存档/QA-EXT/第二章-Alpaca-Ext.json", 10))
    array.extend(random_copy_qa("存档/QA-EXT/第三章-Alpaca-Ext.json", 10))
    array.extend(random_copy_qa("存档/QA-EXT/第四章-Alpaca-Ext.json", 10))
    array.extend(random_copy_qa("存档/QA-EXT/第五章-Alpaca-Ext.json", 10))
    array.extend(random_copy_qa("存档/QA-EXT/第六章-Alpaca-Ext.json", 10))
    array.extend(random_copy_qa("存档/QA-EXT/尾-Alpaca-Ext.json", 3))
    write_json_array_to_file(array, "evaluation.json")


def llm_evaluation(q: str, a1: str, a2: str):
    system_template = """
    你是一位智能助教系统。我会提供给你:
    1. 一个标准的问题和答案对
    2. 学生对该问题的回答

    标准问答对:
    问题: {q}
    标准答案: {a1}

    学生回答:
    {a2}

    你的任务是:
    1. 仔细阅读上述标准问答对和学生的回答
    2. 比较学生的回答与标准答案
    3. 给学生的回答评分(满分100分)
    4. 提供简要的评语,解释评分理由

    评分标准:
    - 内容准确性(60分):回答中的关键点与标准答案的匹配程度
    - 表达清晰度(20分):语言是否清晰、连贯、易懂
    - 回答完整性(20分):是否涵盖了问题的所有方面

    请以JSON格式输出你的评估,包含以下字段:
    - question: 原问题(字符串)
    - standard_answer: 标准答案(字符串)
    - student_answer: 学生回答(字符串)
    - score: 总分(整数)
    - accuracy: 内容准确性得分(整数)
    - clarity: 表达清晰度得分(整数)
    - completeness: 回答完整性得分(整数)
    - comment: 评语(字符串)

    JSON输出示例:
    {{
    "question": "请简述光合作用的过程。",
    "standard_answer": "光合作用是植物利用光能将二氧化碳和水转化为葡萄糖和氧气的过程。主要包括光反应和暗反应两个阶段...",
    "student_answer": "光合作用是植物利用阳光制造食物的过程,主要发生在叶绿体中...",
    "score": 85,
    "accuracy": 50,
    "clarity": 18,
    "completeness": 17,
    "comment": "回答准确把握了主要观点,表达比较清晰。但在[某方面]还可以进一步完善。"
    }}

    请确保你的评分和反馈公正、客观,并具有建设性。
    """
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template)]
    )
    chain = prompt_template | llm | StrOutputParser()
    result = chain.invoke({
        "q": q,
        "a1": a1,
        "a2": a2
    })
    return result


def evaluation(file_path: str):
    score_array = []
    with open(file_path, 'r', encoding='utf-8') as file:
        json_array = json.load(file)
        for item in json_array:
            log("q: "+item["instruction"]+"\n")
            log("a1: "+item["output"]+"\n")
            result = llm_evaluation(
                item["instruction"],
                item["output"],
                user_answer(item["instruction"]))
            log("score: "+result+"\n")
            try:
                score_array.append(json.loads(result))
            except Exception as e:
                log(result)
                log(f"捕获到异常: {e}")
    write_json_array_to_file(score_array, 'evaluation_result.json')


def user_answer(q: str):
    return response("http://10.1.11.201:50002", "app-pCfnpPEvnrT1Sgnds6wRftKh", q)


def response(url: str, api_key: str, q: str):
    url = f'{url}/v1/chat-messages'
    headers = {
        'Authorization': 'Bearer ' + api_key,
        'Content-Type': 'application/json'
    }
    data = {
        "inputs": {},
        "query": q,
        "response_mode": "blocking",
        "conversation_id": "",
        "user": "test",
        "files": []
    }

    success = False
    response = None
    while (not success):
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if (response.status_code == 200):
            success = True

    answer = response.json()["answer"]
    log("a2: "+answer+"\n")
    return answer


def tally_score(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        json_array = json.load(file)
        scores = [item['score'] for item in json_array]
        # 计算平均分
        average_score = sum(scores) / len(scores)
        # 计算高于80分的个数
        above_80_count = sum(1 for score in scores if score > 80)
        # 计算低于60分的个数
        below_60_count = sum(1 for score in scores if score < 60)
        log(f"总数: {len(scores)}")
        log(f"平均分: {average_score}")
        log(f"高于80分的个数: {above_80_count}")
        log(f"低于60分的个数: {below_60_count}")


def log(log: str):
    logger.info(log)


if __name__ == '__main__':
    # generate_random_qa()
    # evaluation("evaluation.json")
    tally_score("evaluation_result.json")
