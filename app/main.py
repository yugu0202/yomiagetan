from pathlib import Path
import os
import json
import discord
from discord.ext import commands

from voicevox_core import VoicevoxCore

intents = discord.Intents.all()
bot: commands.Bot = commands.Bot(command_prefix="!", intents=intents)

json_path = Path("/settings.json")

core = VoicevoxCore(open_jtalk_dict_dir=Path("./open_jtalk_dic_utf_8-1.11"))
speaker_id = 68 #あいえるたん

@bot.event
async def on_ready():
  print(f"Logged in as {bot.user}")

@bot.event
async def on_guild_join(guild):
  with open(json_path, "r") as f:
    settings = json.load(f)

  settings[guild.id] = {"track_channel_ids": []}

  with open(json_path, "w") as f:
    json.dump(settings, f)


@bot.event
async def on_message(message):
  if message.author.id == bot.user.id:
    return

  with open(json_path, "r") as f:
    settings = json.load(f)

  guild_id_string = str(message.guild.id)
  track_channel_ids = settings[guild_id_string]["track_channel_ids"] if settings.get(guild_id_string) is not None else []
  if message.channel.id in track_channel_ids and not message.content.startswith("!"):
    if message.attachments:
      for attachment in message.attachments:
        if attachment.filename.endswith(".wav"):
          return

    if message.embeds:
      for embed in message.embeds:
        if embed.type == "video":
          return

    if message.guild.voice_client is None:
      return

    if not core.is_model_loaded(speaker_id):
      core.load_model(speaker_id)
    wave_bytes = core.tts(message.content, speaker_id)
    with open("temp.wav", "wb") as f:
      f.write(wave_bytes)
    voice_client = message.guild.voice_client
    voice_client.play(discord.FFmpegPCMAudio("temp.wav"))

  await bot.process_commands(message)


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

#特定のチャンネルのメッセージを追跡を設定する
@bot.command()
async def track(ctx, *, text: str):
  print(text)
  channel = discord.utils.get(ctx.guild.text_channels, id=int(text.strip('<#').strip('>')))
  if channel is None:
    await ctx.send(f"チャンネル {text} が見つかりません")
    return

  await ctx.send(f"{channel.name} を追跡します")

  with open(json_path, "r") as f:
    settings = json.load(f)

  track_channel_ids = settings[ctx.guild.id]["track_channel_ids"] if settings.get(ctx.guild.id) else []
  track_channel_ids.append(channel.id)

  if settings.get(ctx.guild.id) is None:
    settings[ctx.guild.id] = {}

  settings[ctx.guild.id]["track_channel_ids"] = track_channel_ids

  with open(json_path, "w") as f:
    json.dump(settings, f)


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