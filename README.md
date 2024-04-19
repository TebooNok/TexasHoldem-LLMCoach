# TexasHoldem-LLMCoach
A simple CMD-based Texas Hold'em game allows play with LLM player and support/coach by a LLM coach.
As the game process is full-text, this is easy to incorporate with llm training like reflexion, expel, react, agent-pro, or even rlcards

You can simply set your api-key and api-url in ```.env```, then start to play by running ```poker_game.py```

We noticed that, using "icon" to represent cards outperform using english/chinese character or words. e.g., ♥K

A sample game in game log is:
```
欢迎使用双人无限制德州扑克-CMD版
是否使用默认配置进行游戏？（即透明模式，显示AI策略，无AI教练；10k初始筹码； 100大盲注） Y/N: N
你是否需要AI玩家生成策略？（不生成会提高速度但降低一些AI水平） Y/N: Y
是否打印AI玩家的策略？ Y/N: Y
您是否需要AI教练？ Y/N: Y
请输入双方的总筹码(至少为1000)：1000
请输入大盲注(至少为10)： 100
游戏开始。
玩家初始筹码：AI - 1000, Human - 1000。

第 1 轮开始：
本轮玩家顺序：human, ai。
小盲注：50，大盲注：100。
human is Small blind. human player 投入 50 小盲注。
ai is Big blind. ai player 投入 100 大盲注。
当前奖池：150。
当前奖池：150。

开始Pre-Flop环节。
当前由 human player 行动。当前奖池为 150。
思考中...
以下是助手的提示信息：
我们手中的底牌是♥K, ♦K，这是非常强的起手牌，通常被称为“口袋国王”。在头对头的德州扑克中，这种牌型给我们提供了极大
的优势。根据一般的概率计算，口袋国王在未见公共牌前赢得底池的概率大约为82%对抗任一随机手牌。我们的目标是最大化利用这个
优势，尽可能地从对手那里赢取更多的筹码。由于我们是小盲位，对手可能会认为我们的加注是试图利用位置优势而进行的标准加注，因
此，我们可以通过较大的加注来隐藏我们手牌的强度，同时也为建立一个大底池打下基础。考虑到当前的盲注水平和双方的筹码深度，我
建议加注到至少3倍大盲注，即300筹码。这样的加注量足以表明我们手中有强牌，同时也给予对手足够的空间来进行错误的决策，比
如用较弱的手牌跟注。如果对手选择跟注，我们将利用后续的投注轮进一步增加底池。如果对手加注，我们必须准备好进行再加注或全下
，因为我们手中的牌型足够强大，可以在大多数情况下对抗对手的范围。
raise with amount 300

您有什么需要问的吗? Y/N: Y
请输入你的问题： 口袋国王的英语是什么？
思考中...
Pocket Kings

以上是我的解答，请问您还有需要问的吗? Y/N: N
你的底牌为： ♥K, ♦K
Allowed actions: fold, call, raise, raise amount must >= 200 chips
Your action: raise
Enter your bet amount: 300
Human Player 行动：raise，下注额 300。
human 加注 300。奖池更新为 450。
当前由 ai player 行动。当前奖池为 450。
思考中...
以下是AI的决策思路：
在当前的Pre-flop阶段，我们持有的底牌是♦5和♥7，这是一个相对较弱的起手牌。在头对头的无限注德州扑克中，起手牌的
选择范围会比较宽，但♦5和♥7并不在理想的范围内，尤其是在对手加注到300后。我们的底牌没有形成任何高牌、对子或是连牌的
潜力，因此，我们在这个阶段的胜率并不高。根据一般的概率分析，没有强牌的情况下，我们的胜率可能低于50%。考虑到对手的加注
行为可能表示他们持有较强的起手牌，或是试图通过攻击性的玩法来施压。在这种情况下，我们的策略应该是保守的。我们可以选择弃牌
（fold），避免在这一轮投入更多的筹码，以保护我们的筹码堆，等待更好的机会。在头对头的比赛中，筹码管理和选择合适的时机
进攻是非常重要的。虽然弃牌意味着放弃这一轮的胜利机会，但在持有较弱底牌且对手表现出强势的情况下，这是一个理智的选择。

AI Player 决策：行动 fold，下注额 0。
ai 弃牌。human 赢得了 450 筹码的底池。
AI 底牌: ♦5, ♥7。
Human 底牌: ♥K, ♦K。
公共牌: 。
AI 当前筹码： 900
Human 当前筹码： 1100

```
