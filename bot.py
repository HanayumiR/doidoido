import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import json

TOKEN = '' # この中にトークンを追加
CHANNEL_ID_FILE = 'channel_id.json'

# 接続処理
intents = discord.Intents.default()
intents.message_content = True  # メッセージコンテンツの意図を有効にする
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
    print('ログインしたよ')
    await bot.tree.sync()
    print('スラッシュコマンドが同期されたよ。')
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
    await interaction.response.send_message('このチャンネルで月曜日を知らせるよ。')
    if reminder_task is None or reminder_task.done():
        reminder_task = bot.loop.create_task(send_reminder())

# 1分ごとにメッセージを送信する関数
async def send_reminder():
    global channel_id
    while True:
        if channel_id is not None:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send('月曜が近いよ')
                await channel.send(file=discord.File(添付したいファイルのパス))
        await asyncio.sleep(604800)  # 一週間待機

# 返信処理
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content == 'どぅいどぅいどぅ～':
        await message.channel.send('https://twitter.com/ChocodateMonday')

bot.run(TOKEN)
