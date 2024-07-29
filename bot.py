#取得処理
import discord
from discord.ext import commands
import asyncio
import os
import json
from datetime import datetime, timedelta
import requests
import sys

#トークン読み込み関数
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
channel_ids = []  

#チャンネルIDのセーブ&ロード
def load_channel_ids():
    global channel_ids
    if os.path.exists(CHANNEL_ID_FILE):
        with open(CHANNEL_ID_FILE, 'r') as file:
            data = json.load(file)
            channel_ids = data.get('channel_ids', [])
            print(f'チャンネルID {channel_ids}が読み込まれました！')
    else:
        print('CHANNEL_ID_FILEが見つかりません')

def save_channel_ids():
    global channel_ids
    try:
        with open(CHANNEL_ID_FILE, 'w') as file:
            json.dump({'channel_ids': channel_ids}, file)
            print(f'チャンネルID{channel_ids}が保存されました。')
    except Exception as e:
        print(f'{e}によってチャンネルIDの保存に失敗しました。')

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
        global channel_ids
        channel_id = interaction.channel.id
        if channel_id not in channel_ids:
            channel_ids.append(channel_id)
            save_channel_ids()
        await interaction.response.send_message('このチャンネルで月曜日が近いことをお知らせします！')

    @bot.tree.command(name="remove_doidoido", description="/doidoidoで指定したチャンネルへのお知らせを解除します！")
    async def remove_doidoido(interaction: discord.Interaction):
        global channel_ids
        channel_id = interaction.channel.id
        if channel_id in channel_ids:
            channel_ids.remove(channel_id)
            save_channel_ids()
            await interaction.response.send_message('このチャンネルで月曜の通知をしないようにしますね。')
        else:
            await interaction.response.send_message('このチャンネルでお知らせするようにしていませんよ！')

    await bot.tree.sync()
    print('スラッシュコマンドが同期されましたよ。')

@bot.event
async def on_ready():
    print('ログインしました！')
    await add_commands()  
    load_channel_ids()
    if channel_ids:
        print(f'チャンネル通知設定が読み込まれましたよ。: {channel_ids}')
        bot.loop.create_task(send_reminder())
    bot.loop.create_task(check_for_reload())
    await bot.change_presence(activity=discord.Game(name="どぅいどぅいどぅ～"))

#指定日時メッセージ送信関数
async def send_reminder():
    global channel_ids
    while True:
        if channel_ids:
            now = datetime.now()
            target_time = now.replace(hour=19, minute=0, second=0, microsecond=0)
            if now.weekday() == 6 and now >= target_time:
                target_time += timedelta(days=7)
            delta = (target_time - now).total_seconds()
            await asyncio.sleep(delta)
            for channel_id in channel_ids:
                channel = bot.get_channel(channel_id)
                if channel:
                    if is_holiday(target_time + timedelta(days=1)):
                        await channel.send('# プロデューサーさん、明日は祝日ですよ！')
                        print(f'#{channel_id}に祝日をお知らせしました！')
                        await channel.send('https://video.twimg.com/ext_tw_video/1784235969786544128/pu/vid/avc1/1280x720/6oz_WapWCOm65c7g.mp4')
                        await asyncio.sleep(24 * 3600)
                        await channel.send('# 火曜日が近いです！')
                        print(f'#{channel_id}に火曜が近いことをお知らせしました！')
                        await channel.send('https://video.twimg.com/ext_tw_video/1784882462671122432/pu/vid/avc1/1280x720/R3qitGqYlpd8dqmH.mp4')
                    else:
                        await channel.send('# 月曜が近いです！')
                        print(f'#{channel_id}に月曜が近いことをお知らせしました！')
                        await channel.send('https://video.twimg.com/ext_tw_video/1779366668697055233/pu/vid/avc1/1280x720/tIK_0IgHkJNaL5Qf.mp4')
            target_time += timedelta(days=7)
        await asyncio.sleep(7 * 24 * 3600)

#返信処理
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    print(f' {message.content}') 
    if message.content == 'どぅいどぅいどぅ～':
        await message.channel.send('https://twitter.com/ChocodateMonday')
        print('どぅいどぅいどぅ～に反応しました！')  
    if message.content == '月曜が近いよ':
        await message.channel.send('https://youtu.be/XvE1VbeLqtg?si=LsL9MgPR4oZ5p4ap')
        print('月曜が近いよに反応しました！')

#リロード処理
async def check_for_reload():
    loop = asyncio.get_event_loop()
    while True:
        input_text = await loop.run_in_executor(None, input, "")
        if input_text.lower() == "reload":
            print("再起動中です...")
            os.execv(sys.executable, ['python'] + sys.argv)

bot.run(TOKEN)
