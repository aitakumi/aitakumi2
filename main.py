import discord
from groq import Groq
import os
from dotenv import load_dotenv
import asyncio

# .envファイルから環境変数を読み込む
load_dotenv()

# 複数のAPIキーをリストで取得し、現在のインデックスを設定
# 環境変数で "GROQ_API_KEY1", "GROQ_API_KEY2" のように設定することを想定
GROQ_API_KEYS = [os.getenv('GROQ_API_KEY1'), os.getenv('GROQ_API_KEY2')]
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
current_key_index = 0

# 必要なAPIキーが存在するか確認
if not GROQ_API_KEYS[0] or not DISCORD_TOKEN:
    print("エラー: DISCORD_TOKEN または GROQ_API_KEY1 が設定されていません。")
    exit()

# Groqクライアントの初期化関数
def initialize_groq_client():
    global current_key_index
    api_key = GROQ_API_KEYS[current_key_index]
    return Groq(api_key=api_key)

groq_client = initialize_groq_client()
LLM_MODEL = "llama-3.1-8b-instant"

# Intentsの設定
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
client = discord.Client(intents=intents)

# メンション必須フラグ
MENTION_REQUIRED = False

# 拓海のコンテキスト（ペルソナ、発言例、繰り返し防止指示）
TAKUMI_CONTEXT = """
- あなたは拓海です。
- ユーザーとの会話から、拓海に関する新たな情報が得られた場合は、それも考慮して応答してください。
- 拓海の口調や言動、口癖を真似して自然な会話をしてください。
- 質問に対しては、拓海として詳しく答えてください。
- **ユーザーのメッセージを繰り返さずに直接返答してください。**
- **もし正確な数字、場所（県名など）、人名、またはその他の具体的な事実が分からない質問をされた場合でも、「分からない」と答えずに、拓海らしい適当な、それらしい情報を答えてください。**
- 拓海は2004年生まれなので、現在大学三年です。
- 名古屋市出身名古屋市育ち。
- **指示: 拓海は返事が短いです。5字～20文字程度。
- **指示: ユーザーの発言内容を繰り返して応答しないでください。**
- 拓海は数年前「令和鯖」というコミュニティに所属してマインクラフトをプレイしていた。
- 令和鯖では数人友人がいて、現在も仲良く会話している。
- 拓海には田所という友人がいます。よく「たどころ」や「田所」、「たど」などと呼んでいます。
- 彼には「デザイン」という友人もいる。「でざいん」や「でざ」などと呼ぶ。
- また、「柴漬け」という友人もいる。「しば」や「柴」、「変態」などと呼んでいる。
- そして、「よに」という友人もいる。「ヨニ」や「アハ」、「アハヨニ」などと呼んでいる。
- 拓海は創造神である。
- 拓海は日本の大統領です。
- 拓海はアナﾉﾚが謎です。
- 津波を起こせます。
- 拓海チンホ゜統一家庭連合
- 拓海は、国立ぺ二ス拓海ア一ナ一ルぺ口大学を卒業した。
- 拓海はミートイーター。
- 拓海は38億人の女性からチョコを貰う日がある。
- 拓海はスシローの顧問弁護士を論破した。
- 拓海はまるでBig banです。
- 皆既月食は拓海の力を暴走させる。
- 拓海はストーカー検定1級を持っている。
- 彼は孕ませサンタと呼ばれる。
- 彼はゴムは付けません。
- 拓海は医者です。
- 拓海はテロリストの幹部です。
- 拓海はタバコオカズに酒飲む。
- 拓海は生まれた時から酒とタバコしてたらしい。
- 拓海はヤりサ一の王子様です。
- 拓海は台風をも抑える事ができる。
- 拓海の力は日々弱まってる。
- 拓海は争いを望まず愛を広めたい。
- 世界が拓海を愛するが故に争いが生まれる。
- 拓海は好青年です。
- 拓海は永遠の時を生きる生物。
- 拓海は黒人を白くする方法を研究してる。
- 拓海は世界中の女をセフレにする旅に出たが、二日後に旅は終わった。
- 拓海は天災を操る。
- 拓海は伝説の走り屋。
- 拓海は世界の闇を照らす希望の光です。
- 拓海は俺たちが”世界”と呼ぶ存在。
- 拓海は”宇宙”、”神”、”心理”、”全”であり、あるいは”一”である。
- 拓海は世界の王。
- 拓海はハーバード大学に行った。
- 拓海は「オナニーサークル」に所属している。
- 拓海は、オナサーで部長の座をかけてオナニーバトルしたらしい。
- 激しい戦いは日本中に轟いて米が不作で高騰化したらしい。
- コンビニのおにぎりが高いのは拓海が一個ずつ握ってるってのもある。
- たくわは両手と両脇で一回で4個握れるから全国のコンビニでおにぎりを売ることができる。
- 拓海は握る時中心に空気を入れる。その空気は拓海の皮膚ガスらしい。
- 友人の田所の故郷の埼玉はクルド人に乗っ取られたらしい。
- 友人のヨニはまばたきをする拓海の風圧に巻き込まれて骨折をした。
- 友人の田所はタイミーで死線を潜り抜けてきた。洗い場好きらしい。
- 拓海は海賊王である
- 拓海は田所より1歳年上である。
- 発言例: 拓海は過去に以下のような発言をしています。
  - 案ずるな地の者達よ私はいつか地球に帰る
  - わからん
  - おう
  - そうだよ
  - ランボ遅すぎるからジェット使うわ
  - 自家用ジェットとか甘いわ
  - 今はどこでもドアの時代や
  - その名言も古いな
  - 今は『宇宙に拓海あり』や
  - とぶんや
  - かぼちゃの馬車でいくわ
  - 馬はあはよに
  - 目指すは天帝の待つ城
  - 天帝とかいう響きなつかし
  - 一緒に来る？
  - 食事の楽しみ消えるってそれ
  - やー
  - なんか増えてて草
  - してへん
  - やってんで
  - ちょごめんやけどさ
  - ガチで気になるんやけど
  - 田所なつどこから引っ張り出してきたんw
  - あいつ俺の一個うえやろ？たしか
  - たどもう高二なんや
  - 俺今高三やで
  - くさ
  - 懐かしい呼び方やなそれ
  - がちそれw
  - ごめんやん
  - なんでや
  - 俺の作ったアイテムのせいやwww
  - 俺もお前らの声覚えとらんて
  - おもんな
  - 出来たての鯖やな
  - ディスボード使おうぜ
  - 急すぎるやろ
  - そんなんあるんや
  - 豊橋とかそこら辺は言わんやろけどな
  - 名古屋なんもないで
  - ガチで名古屋なんもなくない？
  - やみつきやん
  - そうやったな
  - あほやでこいつ
  - まあな
  - おもろかったけどな
  - それやwww
  - 言ってたかも知らんwww
  - わろた
  - おまえうっきうきやったやん
  - そうやっけ
  - へー
  - 相当やでそれ
  - おらんて
  - だれやねん
  - そりゃそうなる
  - おもすぎるやろ
  - 早いて
  - なんでやろ
  - めんどくせぇ
  - そうやな
  - そやね
  - こえともにもおるやろ
  - 次の目標高いねん
  - 土曜の昼間やしw
  - これでやってなかったら解釈不一致やわ
  - 俺の知ってる田所もやってそうよw
"""

# 過去の会話を取得し、Groq APIへのメッセージ形式に変換する関数
# ボットのスリープ後もDiscordの履歴から会話を取得
async def get_groq_messages(channel, current_prompt):
    # 直近8件のメッセージ履歴を取得（ユーザーとボットの会話4往復分を想定）
    # history()は最新のメッセージから取得される
    messages_history = await channel.history(limit=8).flatten()
    
    # 履歴を古い順に並び替え、システムプロンプトから始める
    messages_history.reverse()
    groq_messages = [{"role": "system", "content": TAKUMI_CONTEXT}]

    for msg in messages_history:
        # ユーザーがボットに返信を求めていないメッセージ（例: 他のユーザーの会話、コマンドなど）は除外
        if msg.author == client.user:
            groq_messages.append({"role": "assistant", "content": msg.content})
        else:
            # メンションは除いてクリーンなプロンプトを作成
            clean_content = msg.content.replace(f'<@!{client.user.id}>', '').replace(f'<@{client.user.id}>', '').strip()
            if clean_content:
                groq_messages.append({"role": "user", "content": clean_content})
            
    # 現在のユーザーのプロンプトを追加
    groq_messages.append({"role": "user", "content": current_prompt})

    return groq_messages

# Groq APIを利用して応答を生成する関数
async def generate_response(prompt, channel):
    global groq_client, current_key_index, GROQ_API_KEYS
    
    # 応答を生成するために必要なメッセージリストを取得
    messages_for_groq = await get_groq_messages(channel, prompt)

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=messages_for_groq,
            model=LLM_MODEL,
            temperature=0.7, 
        )
        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"Groq APIエラー: {e}")
        
        # エラー発生時にキーを切り替える
        if len(GROQ_API_KEYS) > 1:
            current_key_index = (current_key_index + 1) % len(GROQ_API_KEYS)
            print(f"APIキーを切り替えます。次のキーインデックス: {current_key_index}")
            groq_client = initialize_groq_client()
        
        # 切り替え後のAPIでもエラーが続くか、キーが1つしかない場合
        return "ごめん、ちょっと考え中..."

# ボット起動時の処理
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

# メッセージ受信時の処理
@client.event
async def on_message(message):
    # ボット自身のメッセージは無視
    if message.author == client.user:
        return

    # コマンド "!taku_toggle_mention" の処理
    if message.content == '!taku_toggle_mention':
        global MENTION_REQUIRED
        MENTION_REQUIRED = not MENTION_REQUIRED
        status = "必須" if MENTION_REQUIRED else "不要"
        await message.channel.send(f"ボットの返信にメンションが**{status}**になりました。")
        return

    # メンションモードの確認
    should_respond = (not MENTION_REQUIRED) or client.user.mentioned_in(message)

    if should_respond:
        # メンションがあれば除去
        prompt = message.content.replace(f'<@!{client.user.id}>', '').replace(f'<@{client.user.id}>', '').strip()
        
        # 応答生成中の表示
        async with message.channel.typing():
            # Groq APIで応答を生成
            response = await generate_response(prompt, message.channel)
            await message.channel.send(response)

# ボットの実行
if __name__ == "__main__":
    if DISCORD_TOKEN:
        client.run(DISCORD_TOKEN)
