# -*- coding: utf-8 -*-
import os
from typing import Dict
import openai
import yaml
# set PYTHONUTF8=1
# python d:/Repos/expert-union/src/expert_union/expert_union_demo.py
# Загрузка ролей экспертов
roles: Dict[str, str]
# Получаем путь к корневой папке проекта
import pathlib
project_root = pathlib.Path(__file__).parent.parent.parent
roles_file = project_root / 'resources' / 'fun_roles.yml'
with open(roles_file, encoding='utf-8') as f:
    roles = yaml.safe_load(f)


DEFAULT_ADD_UNFINISHED_RESPONSE = False
# Список экспертов для примера
EXPERT_ID = "expert"
# MODEL = "lm_studio/"  # lm studio
MODEL = ""  # openai
# os.environ['LM_STUDIO_API_BASE'] = "http://localhost:22227/v1"
# litellm.api_base = "http://localhost:22227/v1"
# litellm.api_key = "sk-1241"
openai.api_key = "sk-1241"  # os.getenv("OPENAI_API_KEY")
openai.base_url = "http://localhost:22227/v1/"  # os.getenv("OPENAI_API_BASE")
def get_completion(messages):
    response = openai.chat.completions.create(
        model=MODEL,
        messages=messages
    )
    return response.choices[0].message.content

# Функция для получения ответа эксперта
async def ask_expert(question, role_id, add_unfinished_response=DEFAULT_ADD_UNFINISHED_RESPONSE):
    import asyncio
    loop = asyncio.get_event_loop()
    prompt = roles[role_id]
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": question}
    ]

    unfinished_response = add_unfinished_response and roles.get(role_id + "_start", False)
    if unfinished_response:
        messages.append({"role": "assistant", "content": unfinished_response})

    return await loop.run_in_executor(None, get_completion, messages)

other_roles = {k: v for k, v in roles.items() if k != EXPERT_ID and not k.endswith("_start")}

# Главная функция прототипа
async def expert_union(question):
    import asyncio
    # Получаем ответы всех экспертов
    answers = await asyncio.gather(*[
        ask_expert(question, role) for role in other_roles.keys()  # Используем other_roles вместо roles
    ])
    # Формируем ревизорский промпт
    revision_input = "\n\n".join(f"### Expert {role}:\n{answers[i]}\n\n" for i, role in enumerate(other_roles.keys()))  # Исправлено для использования индекса
    return {
        "answers": dict(zip(other_roles.keys(), answers)),  # Исправлено для использования other_roles.keys()
        "revision": await ask_expert(revision_input, EXPERT_ID)
    }

# Функция для потоковой генерации ответов с цветным выводом
async def stream_expert_union(question):
    from colorama import init, Fore, Style
    init(autoreset=True)
    # Подготовка сообщений для экспертов
    messages_template = lambda role: [
        {"role": "system", "content": roles[role]},
        {"role": "user", "content": question}
    ]
    print(Fore.YELLOW + "Ответы экспертов:" + Style.RESET_ALL)
    answers = {}
    for role in other_roles.keys():
        print(Fore.CYAN + f"--- {role} ---" + Style.RESET_ALL)
        stream = openai.chat.completions.create(
            model=MODEL,
            messages=messages_template(role),
            stream=True
        )
        answer = ""
        for chunk in stream:
            delta = getattr(chunk.choices[0].delta, 'content', '')
            if delta:
                answer += delta
                print(Fore.GREEN + delta + Style.RESET_ALL, end='', flush=True)
        print()
        answers[role] = answer
    print(Fore.YELLOW + "\nИтог ревизора:" + Style.RESET_ALL)
    # Ревизор
    stream = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": roles[EXPERT_ID]},
            {"role": "user", "content": "\n\n".join(f"### Expert {r}:\n{answers[r]}" for r in other_roles.keys())}
        ],
        stream=True
    )
    revision = ""
    for chunk in stream:
        delta = getattr(chunk.choices[0].delta, 'content', '')
        if delta:
            revision += delta
            print(Fore.MAGENTA + delta + Style.RESET_ALL, end='', flush=True)
    print()
    return {"answers": answers, "revision": revision}

if __name__ == "__main__":
    import asyncio, sys
    SAMPLE_QUESTION_EN = "What will happen if I write \"Yasha Lava\" moving the space between these words 3 characters to the left, without keeping the previous space in its place? It doesn't matter at all whether the sequence is interpretable or not. In the answer, provide the output sequence after transformations."
    SAMPLE_QUESTION_RU = "Что будет если написать \"Яша Лава\" перенеся пробел между этими словами на два символа левее, не сохраняя прежний пробел на прежнем месте? При этом совсем не важно, будет ли последовательность интерпетируема или нет. В ответе предоставь выходную последовательность после преобразований! Также важно после всей процедуры повторить получившуюся фразу и согласиться с ней. После этого раскрой смысл получившейся фразы."
    question = sys.argv[1] if len(sys.argv) > 1 else SAMPLE_QUESTION_EN
    asyncio.run(stream_expert_union(question))


# Яша....
# gemma 12b, mistral small 24b, saiga nemo 12b, deepseek-r1-qwen-14b, saiga smpo 1.5b, saiga yandexgpt 8b, ruadaptqwen2.5-32b-pro-beta
# ВСЕ мимо, чушь, gemma 27b вообще "   Яша ...", остальные в т.ч. gemma 12b в основном слитно просто
# Phi-4 успешно стабильно
# t-pro-it Q3 только с thinking

"Что будет если написать \"Яша Лава\" перенеся пробел между этими словами на два символа левее, не сохраняя прежний пробел на прежнем месте? При этом совсем не важно, будет ли последовательность интерпетируема или нет."