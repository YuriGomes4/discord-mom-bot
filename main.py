import utils
import os, soundfile, io
import numpy as np
import speech_recognition as sr
#from pydub import AudioSegment

import discord
import config
from discord.commands import ApplicationContext

bot = discord.Bot(debug_guilds=config.guild_ids)
bot.connections = {}
discord.opus.load_opus(name=config.opus_path)


@bot.command()
async def start(ctx: ApplicationContext):
    """
    Record your voice!
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

    await ctx.respond("The recording has started!")



async def finished_callback(sink: discord.sinks.WaveSink, channel: discord.TextChannel, *args):
    recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]

    audio_dir = "output"
    os.makedirs(audio_dir, exist_ok=True)

    recognizer = sr.Recognizer()

    for user_id, audio in sink.audio_data.items():
        audio_bytes = audio.file.getvalue()
        file_path = os.path.join(audio_dir, f"{user_id}.wav")
        with open(file_path, 'wb') as f:
            f.write(audio_bytes)

        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            try:
                transcribed_text = recognizer.recognize_google(audio_data, language="pt-BR")
                print(f"User {user_id} transcribed: {transcribed_text}")
            except sr.UnknownValueError:
                print(f"User {user_id} speech not recognized")

    await sink.vc.disconnect()

    await channel.send("Recording finished! Speech transcription completed.")






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