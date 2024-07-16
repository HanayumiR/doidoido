#取得処理
import discord
from discord.ext import commands
import asyncio
import os
import json
from datetime import datetime, timedelta
import requests

#トークン読み込み関数
def load_token():
    with open('token.json', 'r') as file:
        data = json.load(file)
        return data['token']

TOKEN = load_token()  #トークン読み込み
CHANNEL_ID_FILE = 'channel_id.json'
HOLIDAYS_API_URL = 'https://holidays-jp.github.io/api/v1/date.json'

#変数宣言
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

channel_ids = []  #複数のメッセージ送信チャンネルID用保存変数
reminder_task = None  #タスク用保存変数

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
            print(f'チャンネルID{channel_ids}が保存されました')
    except Exception as e:
        print(f'{e}によってチャンネルIDの保存に失敗しました')

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
    load_channel_ids()
    if channel_ids is not None:
        print(f'チャンネル通知設定が読み込まれましたよ。: {channel_ids}')
        global reminder_task
        reminder_task = bot.loop.create_task(send_reminder())
    
    #カスタムステータス設定
    await bot.change_presence(activity=discord.CustomActivity(name="どぅいどぅいどぅ～"))

#スラッシュコマンド定義
@bot.tree.command(name="doidoido", description="このコマンドを使用したチャンネルで月曜が近いことをお知らせします！")
async def doidoido(interaction: discord.Interaction):
    global channel_ids, reminder_task
    channel_id = interaction.channel.id
    if channel_id not in channel_ids:
        channel_ids.append(channel_id)
        save_channel_ids()
    await interaction.response.send_message('このチャンネルで月曜日が近いことをお知らせします！')
    if reminder_task is None or reminder_task.done():
        reminder_task = bot.loop.create_task(send_reminder())

#指定日時メッセージ送信関数
async def send_reminder():
    global channel_ids
    while True:
        if channel_ids:
            #日曜日の19:00をカウント
            now = datetime.now()
            target_time = now.replace(hour=19, minute=0, second=0, microsecond=0)
            if now.weekday() == 6 and now >= target_time:
                #現時刻が日曜日の19:00以降の場合は次週まで待機
                target_time += timedelta(days=7)
            delta = target_time - now
            await asyncio.sleep(delta.total_seconds())
            for channel_id in channel_ids:
                channel = bot.get_channel(channel_id)
                if channel:
                    #明日が祝日の場合
                    if is_holiday(target_time + timedelta(days=1)):
                        await channel.send('明日は祝日です！')
                        await channel.send('https://video.twimg.com/ext_tw_video/1784235969786544128/pu/vid/avc1/1280x720/6oz_WapWCOm65c7g.mp4')
                        #祝日だった場合、翌日の月曜日にお知らせする
                        await asyncio.sleep(24 * 3600)
                        await channel.send('火曜日が近いです！')
                        await channel.send('https://video.twimg.com/ext_tw_video/1784882462671122432/pu/vid/avc1/1280x720/R3qitGqYlpd8dqmH.mp4')
                    #そうではない場合
                    else:
                        await channel.send('月曜が近いです！')
                        await channel.send('https://video.twimg.com/ext_tw_video/1779366668697055233/pu/vid/avc1/1280x720/tIK_0IgHkJNaL5Qf.mp4')
            #送信完了時次週まで待機
            target_time += timedelta(days=7)
        #1時間ごとにチェック
        await asyncio.sleep(3600)  

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
