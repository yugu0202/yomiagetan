from pathlib import Path
import os
import discord
from discord.ext import commands

from voicevox_core import VoicevoxCore

intents = discord.Intents.all()
bot: commands.Bot = commands.Bot(command_prefix="!", intents=intents)

core = VoicevoxCore(open_jtalk_dict_dir=Path("./open_jtalk_dic_utf_8-1.11"))
speaker_id = 68 #あいえるたん

@bot.event
async def on_ready():
  print(f"Logged in as {bot.user}")

@bot.command()
async def join(ctx):
  if ctx.author.voice is None:
    await ctx.send("ボイスチャンネルに参加してから呼んでください")
    return

  await ctx.author.voice.channel.connect()

@bot.command()
async def leave(ctx):
  if ctx.voice_client is None:
    await ctx.send("ボイスチャンネルに参加していません")
    return

  await ctx.voice_client.disconnect()

@bot.command()
async def tts(ctx, *, text: str):
  if ctx.voice_client is None:
    await ctx.send("ボイスチャンネルに参加してから呼んでください")
    return

  if not core.is_model_loaded(speaker_id):
    core.load_model(speaker_id)
  wave_bytes = core.tts(text, speaker_id)
  with open("temp.wav", "wb") as f:
    f.write(wave_bytes)
  voice_client = ctx.voice_client
  voice_client.play(discord.FFmpegPCMAudio("temp.wav"))

bot.run(os.environ["DISCORD_BOT_TOKEN"])