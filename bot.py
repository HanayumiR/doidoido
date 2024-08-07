#取得処理
def load_token():
    with open('token.json', 'r') as file:
        data = json.load(file)
        return data['token']

TOKEN = load_token()

#宣言
CHANNEL_ID_FILE = 'channel_id.json'
HOLIDAYS_API_URL = 'https://holidays-jp.github.io/api/v1/date.json'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
doidoido_channel_ids = []
let_us_go_monday_channel_ids = []
byebye_monday_channel_ids = []

#チャンネルIDのセーブ&ロード
def load_channel_data():
    global doidoido_channel_ids, let_us_go_monday_channel_ids, byebye_monday_channel_ids
    if os.path.exists(CHANNEL_ID_FILE):
        with open(CHANNEL_ID_FILE, 'r') as file:
            data = json.load(file)
            doidoido_channel_ids = data.get('doidoido_channel_ids', [])
            let_us_go_monday_channel_ids = data.get('let_us_go_monday_channel_ids', [])
            byebye_monday_channel_ids = data.get('byebye_monday_channel_ids', [])
            print(f'チャンネルID {doidoido_channel_ids} と Let Us Go Monday チャンネルID {let_us_go_monday_channel_ids} と ByeBye Monday チャンネルID {byebye_monday_channel_ids} が読み込まれました！')
    else:
        print('CHANNEL_ID_FILEが見つかりません')

def save_channel_data():
    global doidoido_channel_ids, let_us_go_monday_channel_ids, byebye_monday_channel_ids
    try:
        with open(CHANNEL_ID_FILE, 'w') as file:
            json.dump({
                'doidoido_channel_ids': doidoido_channel_ids,
                'let_us_go_monday_channel_ids': let_us_go_monday_channel_ids,
                'byebye_monday_channel_ids': byebye_monday_channel_ids
            }, file)
            print(f'チャンネルID {doidoido_channel_ids} と Let Us Go Monday チャンネルID {let_us_go_monday_channel_ids} と ByeBye Monday チャンネルID {byebye_monday_channel_ids} が保存されました。')
    except Exception as e:
        print(f'{e} によってチャンネルデータの保存に失敗しました。')

def get_holidays():
    response = requests.get(HOLIDAYS_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        return {}

holidays = get_holidays()

def is_holiday(date):
    return date.strftime('%Y-%m-%d') in holidays

#スラッシュコマンド定義
async def add_commands():
    @bot.tree.command(name="doidoido", description="このコマンドを使用したチャンネルで月曜が近いことをお知らせします！")
    async def doidoido(interaction: discord.Interaction):
        global doidoido_channel_ids
        doidoido_channel_id = interaction.channel.id
        if doidoido_channel_id not in doidoido_channel_ids:
            doidoido_channel_ids.append(doidoido_channel_id)
            save_channel_data()
        await interaction.response.send_message('このチャンネルで月曜日が近いことをお知らせします！')

    @bot.tree.command(name="remove_doidoido", description="/doidoidoで指定したチャンネルへのお知らせを解除します！")
    async def remove_doidoido(interaction: discord.Interaction):
        global doidoido_channel_ids
        doidoido_channel_id = interaction.channel.id
        if doidoido_channel_id in doidoido_channel_ids:
            doidoido_channel_ids.remove(doidoido_channel_id)
            save_channel_data()
            await interaction.response.send_message('このチャンネルでお知らせしないようにしますね。')
        else:
            await interaction.response.send_message('このチャンネルではお知らせするようにしていませんよ！')

    @bot.tree.command(name="ping", description="反応するまでの時間を計測します！")
    async def ping(interaction: discord.Interaction):
        start_time = datetime.now()
        await interaction.response.send_message('──お疲れ様ですっ！遅くなってすみません！')
        end_time = datetime.now()
        latency = (end_time - start_time).total_seconds() * 1000
        await interaction.followup.send(f' プロデューサーさん、お疲れ様ですっ！応答時間は、えっと…{latency:.2f}ミリ秒です！')

    @bot.tree.command(name="let_us_go_monday", description="このコマンドを使用したチャンネルで月曜日をお知らせします！")
    async def us_go_monday(interaction: discord.Interaction):
        global let_us_go_monday_channel_ids
        channel_id = interaction.channel.id
        if channel_id not in let_us_go_monday_channel_ids:
            let_us_go_monday_channel_ids.append(channel_id)
            save_channel_data()
        await interaction.response.send_message('このチャンネルで月曜日をお知らせします！')

    @bot.tree.command(name="remove_let_us_go_monday", description="/let_us_go_mondayで指定したチャンネルへのお知らせを解除します！")
    async def remove_let_us_go_monday(interaction: discord.Interaction):
        global let_us_go_monday_channel_ids
        channel_id = interaction.channel.id
        if channel_id in let_us_go_monday_channel_ids:
            let_us_go_monday_channel_ids.remove(channel_id)
            save_channel_data()
            await interaction.response.send_message('このチャンネルでお知らせしないようにしますね。')
        else:
            await interaction.response.send_message('このチャンネルではお知らせするようにしていませんよ！')

    @bot.tree.command(name="byebye_monday", description="このコマンドを使用したチャンネルで火曜日のお知らせを解除します！")
    async def byebye_monday(interaction: discord.Interaction):
        global byebye_monday_channel_ids
        channel_id = interaction.channel.id
        if channel_id not in byebye_monday_channel_ids:
            byebye_monday_channel_ids.append(channel_id)
            save_channel_data()
        await interaction.response.send_message('このチャンネルで火曜日をお知らせします！')

    @bot.tree.command(name="remove_byebye_monday", description="/byebye_mondayで指定したチャンネルへのお知らせを解除します！")
    async def remove_byebye_monday(interaction: discord.Interaction):
        global byebye_monday_channel_ids
        channel_id = interaction.channel.id
        if channel_id in byebye_monday_channel_ids:
            byebye_monday_channel_ids.remove(channel_id)
            save_channel_data()
            await interaction.response.send_message('このチャンネルでお知らせしないようにしますね。')
        else:
            await interaction.response.send_message('このチャンネルではお知らせするようにしていませんよ！')

    await bot.tree.sync()
    print('スラッシュコマンドが同期されましたよ。')

@bot.event
async def on_ready():
    print('ログインしました！')
    await add_commands()
    load_channel_data()
    if doidoido_channel_ids:
        print(f'チャンネル通知設定が読み込まれましたよ。: {doidoido_channel_ids}')
        bot.loop.create_task(send_reminder())
    if let_us_go_monday_channel_ids:
        bot.loop.create_task(send_monday_message())
    if byebye_monday_channel_ids:
        bot.loop.create_task(send_byebye_monday_message())
    bot.loop.create_task(check_for_reload())
    await bot.change_presence(activity=discord.Game(name="どぅいどぅいどぅ～"))

#指定日時メッセージ送信関数
async def send_reminder():
    global doidoido_channel_ids
    while True:
        now = datetime.now()
        target_time = now.replace(hour=19, minute=0, second=0, microsecond=0)
        if now.weekday() == 6 and now >= target_time:
            target_time += timedelta(days=7)
        delta = (target_time - now).total_seconds()
        await asyncio.sleep(delta)

        now = datetime.now()
        if now.weekday() == 6:
            for channel_id in doidoido_channel_ids:
                channel = bot.get_channel(channel_id)
                if channel:
                    if is_holiday(now + timedelta(days=1)):
                        await channel.send('# **プロデューサーさん、明日は祝日ですよ！**')
                        print(f'#{channel_id}で祝日をお知らせしました！')
                        await channel.send('https://video.twimg.com/ext_tw_video/1784235969786544128/pu/vid/avc1/1280x720/6oz_WapWCOm65c7g.mp4')
                        await asyncio.sleep(24 * 3600)
                        await channel.send('# **火曜日が近いです！**')
                        print(f'#{channel_id}で火曜日の接近をお知らせしました！')
                        await channel.send('https://video.twimg.com/ext_tw_video/1784882462671122432/pu/vid/avc1/1280x720/R3qitGqYlpd8dqmH.mp4')
                    else:
                        await channel.send('# **月曜日が近いです！**')
                        print(f'#{channel_id}で月曜日の接近をお知らせしました！')
                        await channel.send('https://video.twimg.com/ext_tw_video/1779366668697055233/pu/vid/avc1/1280x720/tIK_0IgHkJNaL5Qf.mp4')
            target_time += timedelta(days=7)
        await asyncio.sleep(7 * 24 * 3600)

async def send_monday_message():
    global let_us_go_monday_channel_ids
    while True:
        now = datetime.now()
        target_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now.weekday() == 0 and now >= target_time:
            target_time += timedelta(days=7)
        delta = (target_time - now).total_seconds()
        await asyncio.sleep(delta)

        now = datetime.now()
        if now.weekday() == 0:
            for channel_id in let_us_go_monday_channel_ids:
                channel = bot.get_channel(channel_id)
                if channel:
                    await channel.send('# **月曜日ですよ！**')
                    print(f'#{channel_id}で月曜をお知らせしました！')
                    await channel.send('https://video.twimg.com/ext_tw_video/1820102073868046336/pu/vid/avc1/1280x720/N0N5xHgFr1cs5s3O.mp4')
            target_time += timedelta(days=7)
        await asyncio.sleep(7 * 24 * 3600)

async def send_byebye_monday_message():
    global byebye_monday_channel_ids
    while True:
        now = datetime.now()
        target_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now.weekday() == 1 and now >= target_time:
            target_time += timedelta(days=7)
        delta = (target_time - now).total_seconds()
        await asyncio.sleep(delta)

        now = datetime.now()
        if now.weekday() == 1:
            for channel_id in byebye_monday_channel_ids:
                channel = bot.get_channel(channel_id)
                if channel:
                    await channel.send('# **火曜です！**')
                    print(f'#{channel_id}で火曜日をお知らせしました！')
                    await channel.send('https://video.twimg.com/ext_tw_video/1800106395586752513/pu/vid/avc1/946x720/Q_EN_ps3Tj7qsElz.mp4')
            target_time += timedelta(days=7)
        await asyncio.sleep(7 * 24 * 3600)

#返信処理
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    print(f'{message.content}') 
    if message.content == 'どぅいどぅいどぅ～':
        await message.channel.send('https://twitter.com/ChocodateMonday')
        print('Twitterのリンクを送信しました！')  
    if message.content == '月曜が近いよ':
        await message.channel.send('https://youtu.be/XvE1VbeLqtg?si=LsL9MgPR4oZ5p4ap')
        print('YouTubeのリンクを送信しました！')
    if message.content == '甘苦いサンデー':
        await message.channel.send('https://nicovideo.jp/watch/sm43779730')
        print('ニコニコ動画のリンクを送信しました！')

#リロード処理
async def check_for_reload():
    loop = asyncio.get_event_loop()
    while True:
        input_text = await loop.run_in_executor(None, input, "")
        if input_text.lower() == "reload":
            print("再起動中です...")
            os.execv(sys.executable, ['python'] + sys.argv)

bot.run(TOKEN)
