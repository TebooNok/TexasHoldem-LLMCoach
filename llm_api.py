import json
import os

import openai
import os
from dotenv import load_dotenv

from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")
client = OpenAI(
    api_key=api_key,
    base_url=api_base
)

def ask_gpt(msg, role, use_json=False, model="gpt-3.5-turbo-1106", histories=None):
    msgs = [{"role": "system",
             "content": role}]
    if histories:
        last_q = histories[0]
        last_a = histories[1]
        msgs.append({"role": "user",
                     "content": last_q})
        msgs.append({"role": "assistant",
                     "content": last_a})
    msgs.append({"role": "user", "content": msg})

    model = model
    # model='gpt-4-1106-preview'
    if model == "gpt-3.5-turbo-1106":
        # reduce msg length to 16k token
        msg = msg[:7000]
    if use_json:
        result = client.chat.completions.create(
            model=model,
            response_format={'type': 'json_object'},
            messages=msgs,
            temperature=0.01,
            stream=False
        )
    else:
        result = client.chat.completions.create(
            model=model,
            # model='gpt-4-32k',
            # model='gpt-4-1106-preview',
            # max_tokens=4000,
            messages=msgs,

            stream=False
        )
    # print(result)
    # return result
    return result.choices[0].message.content


def ask_gpt4(msg, role, history=None, model='gpt-4-0125-preview', temp=0.1, language='zh'):
    temp = temp
    model = model
    print('思考中...')
    if history:
        # support chat history
        msgs = [{"role": "system", "content": role}]
        for his in history:
            question = his[0]
            answer = his[1]
            msgs.append({"role": "user", "content": question})
            msgs.append({"role": "assistant", "content": answer})
        msgs.append({"role": "user", "content": msg})
        result = client.chat.completions.create(
            model=model,
            messages=msgs,
            temperature=temp,
            stream=False,
            response_format={'type': 'json_object'}
        )
    else:
        if language == 'zh':
            msg = '请使用中文输出\n' + msg + '\n输出请使用中文。'
        else:
            msg = 'Please use English output\n' + msg + '\noutput please use English.'
        result = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": role},
                      {"role": "user", "content": msg}],
            temperature=temp,
            stream=False,
            response_format={'type': 'json_object'}
        )

    print('\nFrom gpt: ', result.choices[0].message.content)
    return result.choices[0].message.content


def ask_gpt4_stream(msg, role, history=None, model='gpt-4-0125-preview', temp=0.1, language='zh', json_mode=True):
    temp = temp
    model = model
    additional_params = {'response_format': {'type': 'json_object'}} if json_mode else {}
    print('思考中...')
    if history:
        # support chat history
        msgs = [{"role": "system", "content": role}]
        for his in history:
            question = his[0]
            answer = his[1]
            msgs.append({"role": "user", "content": question})
            msgs.append({"role": "assistant", "content": answer})
        msgs.append({"role": "user", "content": msg})
        result = client.chat.completions.create(
            model=model,
            messages=msgs,
            temperature=temp,
            stream=True,
            **additional_params  # 条件性地添加额外参数
        )
    else:
        if language == 'zh':
            msg = '请使用中文输出\n' + msg + '\n输出请使用中文。'
        else:
            msg = 'Please use English output\n' + msg + '\noutput please use English.'
        msg = msg + '\nIn your output, all terms of Texas Hold\'em, please use English. Do not translate terms of Texas Hold\'em'
        result = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": role},
                      {"role": "user", "content": msg}],
            temperature=temp,
            stream=True,
            **additional_params  # 条件性地添加额外参数
        )
        lines = []
        try:
            for message in result:
                if message.choices[0].delta.content is not None:
                    lines.append(message.choices[0].delta.content)
                    message.choices[0].delta.content = message.choices[0].delta.content.replace('#', '').replace('*', '')
                    yield message.choices[0].delta.content

        finally:
            pass

        print("All lines received from GPT:")
        print("".join(lines))


# 调用函数并处理 Stream 对象
# text = ask_gpt4('help assistance', 'calculate 1+2+3+...+100=? use json format {"progress": [step1, step2,...], "answer": value}')
# print(text)
