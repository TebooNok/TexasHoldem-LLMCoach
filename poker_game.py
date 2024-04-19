import json
import random
from itertools import combinations
from llm_api import ask_gpt4
from llm_utils import *


class PokerGame:
    def __init__(self, gen_ai_plan=True, pt_ai_plan=True, gen_assistant_plan=False, total_chips=10000, big_blind=100):
        # 游戏配置项
        self.chips = {'ai': total_chips, 'human': total_chips}
        self.sb = big_blind // 2
        self.bb = big_blind
        self.print_ai_plan = pt_ai_plan
        self.generate_ai_plan = gen_ai_plan
        self.generate_assistant_plan = gen_assistant_plan

        # 游戏初始化
        self.deck = self.create_deck()
        self.ai_cards = self.deck[:2]
        self.human_cards = self.deck[2:4]
        self.community_cards = []
        self.pot_info = {'pot': 0}
        self.chips_put = {'ai': 0, 'human': 0}
        self.deck = self.deck[4:]
        self.players = ['ai', 'human'] if random.randint(0, 10) > 5 else ['human', 'ai']
        self.round_counter = 1

        # 只记录玩家的动作
        self.human_action_history = []
        self.ai_action_history = []

        # 记录单局游戏进程
        self.game_history = []

        # 记录单局游戏中，AI和助手的计划
        self.ai_plan_history = []
        self.assistant_plan_history = []

        # 记录多局游戏信息，用于性格分析，赛后复盘。
        self.game_history_archive = {}
        self.ai_plan_archive = {}
        self.assistant_plan_archive = {}
        self.human_action_archive = {}
        self.ai_action_archive = {}

    def create_deck(self):
        suits = ['♠', '♥', '♣', '♦']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [f'{suit}{value}' for suit in suits for value in values]
        random.shuffle(deck)
        self.deck = deck
        return deck

    def flush_deck(self):
        self.create_deck()
        self.ai_cards = self.deck[:2]
        self.human_cards = self.deck[2:4]
        self.community_cards = []
        self.deck = self.deck[4:]

    @staticmethod
    def card_value(card):
        values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13,
                  'A': 14}
        return values[card[1:]]
        # if len(card) > 3:
        #     return values[card[:2]]
        # return values[card[1:]] if card[0] in ['黑桃', '红心', '草花', '方片'] else values[card[2:]]

    @staticmethod
    def card_suit(card):
        return card[0]

    @staticmethod
    def is_straight(ranks):
        if len(set(ranks)) != 5:
            return False
        return max(ranks) - min(ranks) == 4 or set(ranks) == {2, 3, 4, 5, 14}

    @classmethod
    def hand_rank(cls, hand):
        ranks = sorted((cls.card_value(card) for card in hand), reverse=True)
        suits = [cls.card_suit(card) for card in hand]
        is_flush = len(set(suits)) == 1
        straight = cls.is_straight(ranks)
        if straight and is_flush:
            return (8 if min(ranks) != 10 else 9, ranks)
        rank_counts = sorted(((ranks.count(rank), rank) for rank in set(ranks)), reverse=True)
        score, high_cards = zip(*rank_counts)
        if score == (4, 1):
            return (7, high_cards)
        if score == (3, 2):
            return (6, high_cards)
        if is_flush:
            return (5, ranks)
        if straight:
            return (4, ranks)
        if score == (3, 1, 1):
            return (3, high_cards)
        if score == (2, 2, 1):
            return (2, high_cards)
        if score == (2, 1, 1, 1):
            return (1, high_cards)
        return (0, ranks)

    @classmethod
    def compare_hands(cls, hand1, hand2):
        rank1, values1 = cls.hand_rank(hand1)
        rank2, values2 = cls.hand_rank(hand2)
        if rank1 != rank2:
            return "Hand1" if rank1 > rank2 else "Hand2"
        else:
            return "Tie" if values1 == values2 else ("Hand1" if values1 > values2 else "Hand2")

    @classmethod
    def best_hand(cls, hole_cards, community_cards):
        return max((cls.hand_rank(comb), comb) for comb in combinations(hole_cards + community_cards, 5))[1]

    def ai_decision(self, allowed_actions, is_preflop=False):
        history_info = '\n'.join(self.game_history)
        ai_history_info = '\n'.join(self.ai_plan_history)
        ai_cards_info = ', '.join(self.ai_cards)
        community_cards_info = ' '.join(self.community_cards)
        legal = '\n'.join(allowed_actions)
        if is_preflop:
            community_cards_info = 'Pre-flop'

        if self.generate_ai_plan:
            role = get_role_with_plan(ai_cards_info, community_cards_info)
            msg = get_msg_with_plan(ai_cards_info, community_cards_info, legal, history_info, ai_history_info)
        else:
            role = get_role_without_plan(ai_cards_info, community_cards_info)
            msg = get_msg_without_plan(ai_cards_info, community_cards_info, legal, history_info)

        result = ask_gpt4(role, msg)
        result = json.loads(result)

        if self.generate_ai_plan:
            self.ai_plan_history.append(result['plan'])
            decision_lines = '\n'.join(
                self.ai_plan_history[-1][i:i + 60] for i in range(0, len(self.ai_plan_history[-1]), 60))
            print('以下是AI的决策思路：\n' + decision_lines + '\n')

        action = result['action']
        if action in ['bet', 'raise']:
            bet_amount = int(result['bet_amount'])
        else:
            bet_amount = 0
        return action, bet_amount

    def ai_assistant(self, allowed_actions, is_preflop=False):
        history_info = '\n'.join(self.game_history)
        assistant_history_info = '\n'.join(self.assistant_plan_history)
        human_cards_info = ', '.join(self.human_cards)
        community_cards_info = ' '.join(self.community_cards)
        legal = '\n'.join(allowed_actions)
        if is_preflop:
            community_cards_info = 'Pre-flop'

        if self.players[0] == 'human':
            position = 'Human player is Small Blind'
        else:
            position = 'Human player is Big Blind'
        role = get_role_assistant_plan(human_cards_info, community_cards_info, position)
        msg = get_msg_assistant_plan(human_cards_info, community_cards_info, legal, history_info, assistant_history_info, position)

        result = ask_gpt4(role, msg)
        result = json.loads(result)

        self.assistant_plan_history.append(result['plan'])
        decision_lines = '\n'.join(
            self.assistant_plan_history[-1][i:i + 60] for i in range(0, len(self.assistant_plan_history[-1]), 60))

        action = result['action']
        if action in ['bet', 'raise']:
            action_line = action + ' with amount ' + str(result['bet_amount'])
        else:
            action_line = action
        return decision_lines + '\n' + action_line

    def assistant_qa(self, question, assistant_plan, allowed_actions, qa_history, is_preflop=False):
        history_info = '\n'.join(self.game_history)
        human_cards_info = ', '.join(self.human_cards)
        community_cards_info = ' '.join(self.community_cards)
        legal = '\n'.join(allowed_actions)
        if is_preflop:
            community_cards_info = 'Pre-flop'

        role = get_qa_role(human_cards_info, community_cards_info)
        msg = get_qa_msg(question, assistant_plan, human_cards_info, community_cards_info, legal, history_info)

        result = ask_gpt4(role, msg, history=qa_history)
        return json.loads(result)['answer']


    def player_action(self, allowed_actions, is_preflop=False):
        least_bet = allowed_actions[-1]
        allowed_actions = allowed_actions[:-1]

        # 在这调用ai辅助，给玩家提供建议。
        if self.generate_assistant_plan:
            assistant_plan = self.ai_assistant(allowed_actions, is_preflop)
            print('以下是助手的提示信息：\n' + assistant_plan + '\n')

            # 允许用户进行交互式提问 - 后面加。
            interactive = input('您有什么需要问的吗? Y/N: ').upper()
            qa_history = []
            while interactive == 'Y':
                question = input('请输入你的问题： ')
                answer = self.assistant_qa(question, assistant_plan, allowed_actions, qa_history, is_preflop)

                qa_history.append((question, answer))
                answer_lines = '\n'.join(
                    answer[i:i + 60] for i in
                    range(0, len(answer), 60))

                print(answer_lines)
                interactive = input('\n以上是我的解答，请问您还有需要问的吗? Y/N: ').upper()

        print("你的底牌为：", ', '.join(self.human_cards))
        print(f"Allowed actions: {', '.join(allowed_actions)}")
        action = input("Your action: ").lower()
        while action not in allowed_actions and action != 'raise' and action != 'bet':
            print("Invalid action. Please choose again.")
            action = input("Your action: ").lower()

        bet_amount = 0
        if action == 'raise' or action == 'bet':
            bet_amount = int(input("Enter your bet amount: "))
            while not bet_amount >= least_bet and bet_amount <= self.chips['human']:
                print("Invalid bet amount. Please enter again.")
                bet_amount = int(input("Enter your bet amount: "))
        return action, bet_amount

    def end_a_round(self):
        self.game_history.append(f"AI 底牌: {', '.join(self.ai_cards)}。")
        print(self.game_history[-1])
        self.game_history.append(f"Human 底牌: {', '.join(self.human_cards)}。")
        print(self.game_history[-1])
        self.game_history.append(f"公共牌: {', '.join(self.community_cards)}。")
        print(self.game_history[-1])
        self.game_history.append(f"AI 当前筹码： {self.chips['ai']}")
        print(self.game_history[-1])
        self.game_history.append(f"Human 当前筹码： {self.chips['human']}")
        print(self.game_history[-1])

    def betting_round(self, is_preflop=False):
        current_bet = self.bb  # 默认为大盲注
        last_raiser = None
        action_complete = False
        last_action = None
        round_name = "Pre-Flop" if is_preflop else "Flop" if len(self.community_cards) == 3 else "Turn" if len(
            self.community_cards) == 4 else "River"
        self.game_history.append(f"开始{round_name}环节。")
        print()
        print(self.game_history[-1])
        check_count = 0
        while not action_complete:
            for player in self.players:
                if last_raiser is not None and last_raiser == player:
                    action_complete = True
                    break
                if check_count == 2:
                    action_complete = True
                    break
                if is_preflop and check_count == 1:
                    action_complete = True
                    break

                allowed_actions = []
                # 澄清一下，raise和bet都是其值直接添加到pot，对手根据和你总下注的筹码进行补齐。 只有pre-flop的第一个动作为call时，才允许raise
                if not last_action:
                    allowed_actions = ['fold', 'check', 'bet', f'bet amount must >= {2 * current_bet} chips']
                    if is_preflop:
                        allowed_actions = ['fold', 'call', 'raise', f'raise amount must >= {2 * current_bet} chips']
                else:
                    if last_action == 'check':
                        allowed_actions = ['fold', 'check', 'raise', f'raise amount must >= {2 * current_bet} chips']
                    if last_action == 'call':
                        allowed_actions = ['fold', 'check', 'raise', f'raise amount must >= {2 * current_bet} chips']
                    if last_action in ['raise', 'bet']:
                        allowed_actions = ['fold', 'call', f'raise amount must >= {2 * current_bet} chips']

                self.game_history.append(f"当前由 {player} player 行动。当前奖池为 {self.pot_info['pot']}。")
                print(self.game_history[-1])
                if player == 'ai':
                    action, bet_amount = self.ai_decision(allowed_actions, is_preflop)
                    if action == 'call':
                        bet_amount = -self.chips_put['ai'] + self.chips_put['human']
                    self.game_history.append(f"AI Player 决策：行动 {action}，下注额 {bet_amount}。")
                    print(self.game_history[-1])
                else:
                    allowed_actions.append(2 * current_bet)
                    action, bet_amount = self.player_action(allowed_actions, is_preflop)
                    if action == 'call':
                        bet_amount = self.chips_put['ai'] - self.chips_put['human']
                    self.game_history.append(f"Human Player 行动：{action}，下注额 {bet_amount}。")
                    print(self.game_history[-1])

                # print(f"{player} action: {action} with bet {bet_amount}")

                if action == 'fold':
                    self.chips[self.players[(self.players.index(player) + 1) % 2]] += self.pot_info['pot']
                    self.game_history.append(
                        f"{player} 弃牌。{self.players[(self.players.index(player) + 1) % 2]} 赢得了 {self.pot_info['pot']} 筹码的底池。")
                    print(self.game_history[-1])
                    return True
                elif action == 'check':
                    self.game_history.append(f"{player} 过牌。")
                    last_action = action
                    print(self.game_history[-1])
                    check_count += 1
                elif action == 'bet' or action == 'raise':
                    # diff = bet_amount - chips_put[player]
                    self.chips_put[player] += bet_amount
                    self.chips[player] -= bet_amount
                    self.pot_info['pot'] += bet_amount

                    current_bet = bet_amount
                    last_raiser = player
                    last_action = action
                    self.game_history.append(
                        f"{player} {'加注' if action == 'raise' else '下注'} {bet_amount}。奖池更新为 {self.pot_info['pot']}。")
                    print(self.game_history[-1])
                elif action == 'call':
                    diff = abs(self.chips_put['ai'] - self.chips_put['human'])
                    self.chips[player] -= diff
                    self.pot_info['pot'] += diff
                    self.chips_put[player] += diff
                    self.game_history.append(
                        f"{player} 跟注到 {self.chips_put[player]}。奖池更新为 {self.pot_info['pot']}。")
                    print(self.game_history[-1])
                    if not is_preflop:
                        action_complete = True
                    last_action = action
                    # if not is_preflop:
                    #     break

        self.game_history.append(f"{round_name}环节结束。当前奖池为 {self.pot_info['pot']}。")
        print(self.game_history[-1])
        return False

    def play_round(self):
        self.game_history.append(f"\n第 {self.round_counter} 轮开始：")
        print(self.game_history[-1])
        self.game_history.append(f"本轮玩家顺序：{', '.join(self.players)}。")
        print(self.game_history[-1])
        # 记录盲注信息
        self.game_history.append(f"小盲注：{self.sb}，大盲注：{self.bb}。")
        print(self.game_history[-1])
        self.chips['ai'] -= self.sb if self.players[0] == 'ai' else self.bb
        self.chips['human'] -= self.sb if self.players[0] == 'human' else self.bb
        self.chips_put['ai'] = self.sb if self.players[0] == 'ai' else self.bb
        self.chips_put['human'] = self.sb if self.players[0] == 'human' else self.bb
        self.pot_info['pot'] = self.sb + self.bb
        self.game_history.append(
            f"{self.players[0]} is Small blind. {self.players[0]} player 投入 {self.sb} 小盲注。")
        print(self.game_history[-1])
        self.game_history.append(f"{self.players[1]} is Big blind. {self.players[1]} player 投入 {self.bb} 大盲注。")
        print(self.game_history[-1])
        self.game_history.append(f"当前奖池：{self.pot_info['pot']}。")
        print(self.game_history[-1])
        # Pre-Flop
        print(self.game_history[-1])
        if self.betting_round(True):
            self.end_a_round()
            return

        # Flop
        self.community_cards += self.deck[:3]
        self.deck = self.deck[3:]
        self.game_history.append(f"Flop: {' '.join(self.community_cards)}。")
        print(self.game_history[-1])
        if self.betting_round():
            self.end_a_round()
            return

        # Turn
        self.community_cards += self.deck[:1]
        self.deck = self.deck[1:]
        self.game_history.append(f"Turn: {' '.join(self.community_cards)}。")
        print(self.game_history[-1])
        if self.betting_round():
            self.end_a_round()
            return

        # River
        self.community_cards += self.deck[:1]
        self.deck = self.deck[1:]
        self.game_history.append(f"River: {' '.join(self.community_cards)}。")
        print(self.game_history[-1])
        if self.betting_round():
            self.end_a_round()
            return

        # Showdown
        human_best = self.best_hand(self.human_cards, self.community_cards)
        ai_best = self.best_hand(self.ai_cards, self.community_cards)
        winner = self.compare_hands(human_best, ai_best)
        self.game_history.append(
            f"Showdown: Human best hand {', '.join(human_best)}, AI best hand {', '.join(ai_best)}。")
        print(self.game_history[-1])

        # self.game_history.append(f"Winner: {'human' if winner == 'Hand1' else 'ai'}。")

        winner = 'human' if winner == 'Hand1' else 'ai'
        self.chips[winner] += self.pot_info['pot']
        self.game_history.append(
            f"{winner} 获胜， 赢得了 {self.pot_info['pot']} 筹码的底池。")
        print(self.game_history[-1])

        self.end_a_round()

    def main(self):
        self.game_history.append("游戏开始。")
        print(self.game_history[-1])
        self.game_history.append(f"玩家初始筹码：AI - {self.chips['ai']}, Human - {self.chips['human']}。")
        print(self.game_history[-1])

        # 游戏的主循环逻辑
        while all(c > 0 for c in self.chips.values()):
            self.play_round()
            # record 单局信息
            self.ai_plan_archive[self.round_counter] = self.ai_plan_history
            self.assistant_plan_archive[self.round_counter] = self.assistant_plan_history
            self.game_history_archive[self.round_counter] = self.game_history
            self.ai_action_archive[self.round_counter] = self.ai_action_history
            self.human_action_archive[self.round_counter] = self.human_action_history

            if not all(c > 0 for c in self.chips.values()):
                break

            self.ai_plan_history = []
            self.assistant_plan_history = []
            self.game_history = []
            self.ai_action_history = []
            self.human_action_history = []
            self.round_counter += 1
            self.players.reverse()  # 交换玩家位置
            self.flush_deck()

        # 游戏完全结束，进行回顾性分析
        print("游戏结束")
        print("以下是游戏的进程记录：")
        print('\n'.join(self.game_history))
        print("以下是AI对手的决策记录：")
        print('\n'.join(self.ai_action_history))
        print("以下是AI对手的思考记录：")
        print('\n'.join(self.ai_plan_history))
        print("以下是教练的辅助记录：")
        print('\n'.join(self.assistant_plan_history))


if __name__ == "__main__":
    print("欢迎使用双人无限制德州扑克-CMD版")
    default_setting = input("是否使用默认配置进行游戏？（即透明模式，显示AI策略，无AI教练；10k初始筹码； 100大盲注） Y/N: ").upper()
    if default_setting == 'Y':
        game = PokerGame()
    else:
        generate_ai_plan = input("你是否需要AI玩家生成策略？（不生成会提高速度但降低一些AI水平） Y/N: ").upper()
        generate_ai_plan = True if generate_ai_plan == 'Y' else False
        if generate_ai_plan:
            print_ai_plan = input("是否打印AI玩家的策略？ Y/N: ").upper()
            print_ai_plan = True if print_ai_plan == 'Y' else False
        else:
            print_ai_plan = False

        generate_assistant_plan = input("您是否需要AI教练？ Y/N: ").upper()
        generate_assistant_plan = True if generate_assistant_plan == 'Y' else False

        try:
            total_chips = int(input("请输入双方的总筹码(至少为1000)："))
            big_blind = int(input("请输入大盲注(至少为10)： "))
            if big_blind < 10 or total_chips < 1000:
                raise ValueError('筹码至少为1000，大盲注最小为10。')
        except Exception as e:
            print('非法数值，程序退出', str(e))
            exit(1)
        game = PokerGame(generate_ai_plan, print_ai_plan, generate_assistant_plan, total_chips, big_blind)
    game.main()
