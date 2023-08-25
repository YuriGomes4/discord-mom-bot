import utils
import os, soundfile, io
import numpy as np
#from pydub import AudioSegment

import discord
import config
from discord.commands import ApplicationContext

import deepspeech

# Carregue o modelo e o arquivo de vocabulário
model_path = "deepspeech-0.9.3-models.pbmm"
scorer_path = "deepspeech-0.9.3-models.scorer"
ds = deepspeech.Model(model_path)
ds.enableExternalScorer(scorer_path)

bot = discord.Bot(debug_guilds=config.guild_ids)
bot.connections = {}
discord.opus.load_opus(name=config.opus_path)


# Função para transcrever o áudio
def transcribe_audio(audio_bytes):
    return ds.stt(audio_bytes)

@bot.command()
async def start(ctx: ApplicationContext):
    """
    Record your voice and transcribe in real-time!
    """
    await ctx.defer()
    sink = discord.sinks.WaveSink()

    voice = ctx.author.voice

    if not voice:
        return await ctx.respond("You're not in a vc right now")

    vc = await voice.channel.connect()
    bot.connections.update({ctx.guild.id: vc})

    vc.start_recording(
        sink,
        finished_callback,
        ctx.channel,
    )

    await ctx.respond("The recording and transcription have started!")




async def finished_callback(sink: discord.sinks.WaveSink, channel: discord.TextChannel, *args):
    audio_data = sink.get_audio_data()

    transcriptions = {}
    for user_id, audio in audio_data.items():
        transcription = transcribe_audio(audio.file.getvalue())
        transcriptions[user_id] = transcription

    await sink.vc.disconnect()

    # Print transcriptions
    for user_id, transcription in transcriptions.items():
        await channel.send(f"<@{user_id}> said: {transcription}")

    await channel.send("Recording and transcription finished!")



@bot.command()
async def stop(ctx):
    """
    Stop recording.
    """
    await ctx.defer()
    if ctx.guild.id in bot.connections:
        vc = bot.connections[ctx.guild.id]
        vc.stop_recording()
        del bot.connections[ctx.guild.id]
        await ctx.delete()
    else:
        await ctx.respond("Not recording in this guild.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}#{bot.user.discriminator}")


bot.run(config.bot_token)