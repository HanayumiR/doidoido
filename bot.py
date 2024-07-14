import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import json

TOKEN = 'UR_DISCORD_TOKEN_IS_HERE' # この中にトークンを追加
CHANNEL_ID_FILE = 'channel_id.json'

# 接続処理
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='/', intents=intents)

channel_id = None  # メッセージを送信するチャンネルIDを保存するための変数
reminder_task = None  # リマインダーのタスクを保存する変数

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

@bot.event
async def on_ready():
    print('ログインしました！')
    await bot.tree.sync()
    print('スラッシュコマンドが同期されました')
    load_channel_id()
    if channel_id is not None:
        print(f'リマインダー設定が読み込まれたよ。: {channel_id}')
        global reminder_task
        reminder_task = bot.loop.create_task(send_reminder())

# スラッシュコマンドの定義
@bot.tree.command(name="doidoido", description="Set the channel for reminders")
async def doidoido(interaction: discord.Interaction):
    global channel_id, reminder_task
    channel_id = interaction.channel.id
    save_channel_id()
    await interaction.response.send_message('このチャンネルで月曜日をお知らせします！')
    if reminder_task is None or reminder_task.done():
        reminder_task = bot.loop.create_task(send_reminder())

async def send_reminder():
    global channel_id
    while True:
        if channel_id is not None:
            channel = bot.get_channel(channel_id)
            if channel:
                # 日曜日の19:00を計算する
                now = datetime.now()
                target_time = now.replace(hour=19, minute=0, second=0, microsecond=0)#19:00に設定 
                if now.weekday() == 6 and now >= target_time:# 日曜日の19:00以降の場合に次の週の日曜日19:00まで待つ
                    target_time += timedelta(days=7)
                delta = target_time - now
                await asyncio.sleep(delta.total_seconds())
                await channel.send('月曜が近いです！')
                await channel.send('https://video.twimg.com/ext_tw_video/1779366668697055233/pu/vid/avc1/1280x720/tIK_0IgHkJNaL5Qf.mp4')
        await asyncio.sleep(3600)  

# 返信処理
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content == 'どぅいどぅいどぅ～':
        await message.channel.send('https://twitter.com/ChocodateMonday')
    if message.content == '月曜が近いよ':
        await message.channel.send('https://youtu.be/XvE1VbeLqtg?si=LsL9MgPR4oZ5p4ap')

bot.run(TOKEN)
