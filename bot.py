#いろいろ取得したりするやつ
import discord
from discord.ext import commands
import asyncio
import os
import json
from datetime import datetime, timedelta
import requests

TOKEN = 'YOUR_DISCORD_TOKEN'
CHANNEL_ID_FILE = 'channel_id.json'
HOLIDAYS_API_URL = 'https://holidays-jp.github.io/api/v1/date.json'

#接続処理
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

channel_id = None  #メッセージ送信チャンネルID用保存変数
reminder_task = None  #タスク用保存変数

def load_channel_id():
    global channel_id
    if os.path.exists(CHANNEL_ID_FILE):
        with open(CHANNEL_ID_FILE, 'r') as file:
            data = json.load(file)
            channel_id = data.get('channel_id')

def save_channel_id():
    global channel_id
    with open(CHANNEL_ID_FILE, 'w') as file:
        json.dump({'channel_id': channel_id}, file)

def get_holidays():
    response = requests.get(HOLIDAYS_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        return {}

holidays = get_holidays()

def is_holiday(date):
    return date.strftime('%Y-%m-%d') in holidays

@bot.event
async def on_ready():
    print('ログインしました！')
    await bot.tree.sync()
    print('スラッシュコマンドが同期されました')
    load_channel_id()
    if channel_id is not None:
        print(f'チャンネル通知設定が読み込まれましたよ。: {channel_id}')
        global reminder_task
        reminder_task = bot.loop.create_task(send_reminder())
    
    # カスタムステータスの設定
    await bot.change_presence(activity=discord.CustomActivity(name="どぅいどぅいどぅ～"))

# スラッシュコマンドの定義
@bot.tree.command(name="doidoido", description="このコマンドを使用したチャンネルで月曜が近いことをお知らせします！")
async def doidoido(interaction: discord.Interaction):
    global channel_id, reminder_task
    channel_id = interaction.channel.id
    save_channel_id()
    await interaction.response.send_message('このチャンネルで月曜日が近いことをお知らせします！')
    if reminder_task is None or reminder_task.done():
        reminder_task = bot.loop.create_task(send_reminder())

#指定日時メッセージ送信関数
async def send_reminder():
    global channel_id
    while True:
        if channel_id is not None:
            channel = bot.get_channel(channel_id)
            if channel:
                #日曜日の19:00をカウント
                now = datetime.now()
                target_time = now.replace(hour=19, minute=0, second=0, microsecond=0)
                if now.weekday() == 6 and now >= target_time:
                    #現時刻が日曜日の19:00以降の場合は次週まで待機
                    target_time += timedelta(days=7)
                delta = target_time - now
                await asyncio.sleep(delta.total_seconds())
                
                #明日が祝日の場合
                if is_holiday(target_time + timedelta(days=1)):
                    await channel.send('明日は祝日です！')
                    await channel.send('https://video.twimg.com/ext_tw_video/1812141628598915072/pu/vid/avc1/1280x720/NWGNABfw5uo3fazF.mp4')
                #そうではない場合
                else:
                    await channel.send('月曜が近いです！')
                    await channel.send('https://video.twimg.com/ext_tw_video/1779366668697055233/pu/vid/avc1/1280x720/tIK_0IgHkJNaL5Qf.mp4')
        await asyncio.sleep(3600)  #1時間ごとにチェック

#返信処理
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content == 'どぅいどぅいどぅ～':
        await message.channel.send('https://twitter.com/ChocodateMonday')
    if message.content == '月曜が近いよ':
        await message.channel.send('https://youtu.be/XvE1VbeLqtg?si=LsL9MgPR4oZ5p4ap')

bot.run(TOKEN)
