import json
import random

from flask import Flask, Response, request, jsonify
from flask_cors import CORS

from llm_api import ask_gpt4, ask_gpt4_stream
from llm_utils import *
from poker_util import hands_potential

app = Flask(__name__)
CORS(app)


@app.route('/poker_chat', methods=['GET'])
def poker_chat():
    cards_info = request.args.get('my_cards', '')
    community_info = request.args.get('community_cards', '')
    chat_info = request.args.get('chat_info', '')
    game_history = request.args.get('game_history', '')
    player_name = request.args.get('player_name', 'ai')
    # game_history = game_history[-80:]
    # chat_info = chat_info[-80:]

    language = request.args.get('language', 'zh')

    int10 = random.randint(0, 10)
    # character = ['特朗普', '罗永浩', '周星驰', '刘德华', '周润发', '冯巩', '郭德纲', '马斯克', '韩寒', '小沈阳', '赵本山'][int10]
    # role = get_chat_role_quick(cards_info, community_info, character)
    # msg = get_chat_msg_quick(chat_info, cards_info, community_info, game_history, character, player_name)

    role = get_chat_role_quick(cards_info, community_info, character='')
    msg = get_chat_msg_quick(chat_info, cards_info, community_info, game_history, character='', player_name='ai')
    # result = ask_gpt4(role, msg, model="gpt-3.5-turbo-1106", temp=1)
    result = ask_gpt4(role, msg, temp=1, language=language)
    chat_msg = json.loads(result)['msg']

    print('角色：', json.loads(result)['character'])
    print('聊天接口的输入信息为：')
    print('my cards: ', cards_info)
    print('community cards: ', community_info)
    print('chat record: ', chat_info)
    print('game info: ', game_history)

    print('回复内容为： ', chat_msg)
    return Response(json.dumps({'message': chat_msg}), mimetype='application/json')


@app.route('/poker_chat_quick', methods=['GET'])
def poker_chat_quick():
    cards_info = request.args.get('my_cards', '')
    community_info = request.args.get('community_cards', '')
    chat_info = request.args.get('chat_info', '')
    game_history = request.args.get('game_history', '')
    player_name = request.args.get('player_name', 'ai')
    language = request.args.get('language', 'zh')
    # game_history = game_history[-80:]
    # chat_info = chat_info[-80:]

    int10 = random.randint(0, 10)
    character = \
        ['特朗普', '罗永浩', '周星驰', '刘德华', '周润发', '冯巩', '郭德纲', '马斯克', '韩寒', '小沈阳', '赵本山'][
            int10]
    role = get_chat_role_quick(cards_info, community_info, character)
    msg = get_chat_msg_quick(chat_info, cards_info, community_info, game_history, character, player_name)

    parts = []

    def generate():
        for part in ask_gpt4_stream(role, msg, model="gpt-3.5-turbo-1106", language=language, temp=1, json_mode=False):
            parts.append(part)
            yield part

    return Response(generate(), mimetype='text/plain')

    # result = ask_gpt4(role, msg, model="gpt-3.5-turbo-1106", temp=1)
    # result = ask_gpt4(role, msg, language=language, temp=1)
    chat_msg = json.loads("".join(parts))['msg']

    print('角色：', json.loads(result)['character'])
    print('聊天接口的输入信息为：')
    print('my cards: ', cards_info)
    print('community cards: ', community_info)
    print('chat record: ', chat_info)
    print('game info: ', game_history)

    print('回复内容为： ', chat_msg)


@app.route('/solo_ai_decision', methods=['GET'])
def solo_ai_decision():
    cards_info = request.args.get('my_cards', '')
    community_info = request.args.get('community_cards', '')
    player_name = request.args.get('player_name', 'AI')
    game_history = request.args.get('game_history', '')
    plan_history = request.args.get('plan_history', '')
    legal_action = request.args.get('legal_actions', '')
    plan = request.args.get('plan', 'true').lower()

    language = request.args.get('language', 'zh')

    if plan == 'true':
        plan = True
    else:
        plan = False
    if plan:
        role = get_role_with_plan(cards_info, community_info, player_name=player_name)
        msg = get_msg_with_plan(cards_info, community_info, legal_action, game_history, plan_history, player_name)
    else:
        role = get_role_without_plan(cards_info, community_info, player_name=player_name)
        msg = get_msg_without_plan(cards_info, community_info, legal_action, game_history, player_name)

    result = ask_gpt4(role, msg, language=language)
    return Response(result, mimetype='application/json')


@app.route('/solo_ai_assistant', methods=['GET'])
def solo_ai_assistant():
    cards_info = request.args.get('my_cards', '')
    community_info = request.args.get('community_cards', '')
    player_name = request.args.get('player_name', 'Human')
    game_history = request.args.get('game_history', '')
    plan_history = request.args.get('plan_history', '')
    legal_action = request.args.get('legal_actions', '')
    position = request.args.get('position', '')

    language = request.args.get('language', 'zh')

    all_cards = cards_info.strip().split(',') + community_info.strip().split(',')
    all_cards = [card for card in all_cards if card != '']

    potential_text = 'Unknown'
    if 2 < len(all_cards) < 7:
        print('Calculating the probability of your hand...', ', '.join(all_cards))
        potential = hands_potential(all_cards)
        potential_text = 'The potential probability of your hand is:\n' + '\n'.join([item[0] + ', ' + "{:.2f}%".format(item[1] * 100) for item in potential['probability']])
        print(potential_text)

    if len(all_cards) == 7:
        # here get best hand
        pass

    print('\n======= Call coach ========\n')
    print('my cards: ', cards_info)
    print('community cards: ', community_info)
    print('game history: ', game_history)
    print('plan history: ', plan_history)
    print('legal actions: ', legal_action)
    print('position: ', position)
    print('player name: ', player_name)

    role = get_role_assistant_plan(cards_info, community_info, position, player_name=player_name)
    msg = get_msg_assistant_plan(cards_info, community_info, legal_action, game_history, plan_history, position,
                                 player_name, potential_text)

    # result = ask_gpt4(role, msg, language=language)
    # return Response(result, mimetype='application/json')
    def generate():
        for part in ask_gpt4_stream(role, msg, language=language, json_mode=False):
            yield part

    return Response(generate(), mimetype='text/plain')


@app.route('/solo_assistant_chat', methods=['GET'])
def solo_assistant_chat():
    question = request.args.get('question', '')
    assistant_plan = request.args.get('assistant_plan', '')
    cards_info = request.args.get('my_cards', '')
    community_info = request.args.get('community_cards', '')
    player_name = request.args.get('player_name', 'Human')
    game_history = request.args.get('game_history', '')
    legal_action = request.args.get('legal_actions', '')
    # chat_history = request.args.get('chat_history', 'q1_mid_a1_|QA|_q2_mid_a2_|QA|_q3_mid_a3')
    language = request.args.get('language', 'zh')

    all_cards = cards_info.strip().split(',') + community_info.strip().split(',')
    all_cards = [card for card in all_cards if card != '']

    potential_text = 'Unknown'
    if 2 < len(all_cards) < 7:
        print('Calculating the probability of your hand...', ', '.join(all_cards))
        potential = hands_potential(all_cards)
        potential_text = 'The potential probability of your hand is:\n' + '\n'.join([item[0] + ', ' + "{:.2f}%".format(item[1] * 100) for item in potential['probability']])
        print(potential_text)

    if len(all_cards) == 7:
        # here get best hand
        pass

    print('\n========= Call assistant chat =========\n')
    print('question: ', question)
    print('assistant_plan: ', assistant_plan)
    print('my cards: ', cards_info)
    print('community cards: ', community_info)
    print('player name: ', player_name)
    print('game history: ', game_history)
    print('legal action: ', legal_action)
    # print('chat history: ', chat_history)
    print('language: ', language)

    # history = []
    # for his in chat_history.split('_|QA|_'):
    #     qa = his.split('_mid_')
    #     history.append([qa[0], qa[1]])

    role = get_qa_role(cards_info, community_info, player_name=player_name)
    msg = get_qa_msg(question, assistant_plan, cards_info, community_info, game_history, player_name=player_name, potential=potential_text)

    # msg += '\nChat history: ' + chat_history
    # result = ask_gpt4(role, msg, history=history)
    # result = ask_gpt4(role, msg, language=language)
    # return Response(result, mimetype='application/json')

    def generate():
        for part in ask_gpt4_stream(role, msg, language=language, json_mode=False):
            yield part

    return Response(generate(), mimetype='text/plain')


@app.route('/ai_guide', methods=['GET'])
def ai_guide():
    cards_info = request.args.get('player_cards', '')  # 所有玩家的信息
    community_info = request.args.get('community_cards', '')  # 公共牌
    player_name = request.args.get('player_name', 'Human')  # 高亮玩家：即将解说的高亮玩家
    player_action = request.args.get('player_action', 'Unknow')  # 该玩家的动作
    game_history = request.args.get('game_history', '')  # 游戏历史
    comment_history = request.args.get('comment_history', '')  # 解说历史（对话历史

    talk_length = request.args.get('talk_length', '20')  # 对话长度
    emotion = request.args.get('emotion', 'neutral')  # 情感
    language = request.args.get('language', 'zh')

    print('\n======= Call AI GUIDE ========\n')
    print('cards_info:', cards_info)
    print('community_info:', community_info)
    print('player_name:', player_name)
    print('player_action:', player_action)
    print('game_history:', game_history)
    print('comment_history:', comment_history)
    print('talk_length:', talk_length)
    print('emotion:', emotion)
    print('language:', language)

    role = get_commentary_role_guide()
    msg = get_commentary_msg_guide(cards_info, community_info, player_name, player_action, game_history, comment_history)

    # result = ask_gpt4(role, msg, language=language, temp=1)
    # return Response(result, mimetype='application/json')
    def generate():
        for part in ask_gpt4_stream(role, msg, language=language, temp=1, json_mode=False):
            yield part

    return Response(generate(), mimetype='text/plain')


@app.route('/ai_guide_short', methods=['GET'])
def ai_guide_short():
    # 读取输入参数
    player_name = request.args.get('player_name', 'Player')  # 当前玩家名称
    player_action = request.args.get('player_action', '')  # 当前玩家动作
    player_cards = request.args.get('player_cards', '')  # 玩家手牌
    community_cards = request.args.get('community_cards', '')  # 公共牌
    language = request.args.get('language', 'zh')

    # 生成解说角色和信息提示词
    role = get_commentary_role_guide_short()
    msg = get_commentary_msg_guide_short(player_name, player_action, player_cards, community_cards)

    # result = ask_gpt4(role, msg, language=language, temp=1)
    # return Response(result, mimetype='application/json')
    def generate():
        for part in ask_gpt4_stream(role, msg, language=language, temp=1, json_mode=False):
            yield part

    return Response(generate(), mimetype='text/plain')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8631)
