import subprocess
import os
import telnetlib
import asyncio
import discord



VER = "2.0.5-R[√]"
TOKEN = '[ここにBotのトークン]'
CHANNEL_ID = [ここにターミナルとして利用するチャンネルIDを]
QEMU_HOST = "127.0.0.1"
QEMU_PORT = 5555
DEBUGMODE = True ## Botコンソール上でQEMUが動作しているかどうかを確認するやつ

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

qemu_writer = None

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    client.loop.create_task(read_from_qemu())
    channel = client.get_channel(CHANNEL_ID)
    await channel.send("============Started =============")
    await channel.send("QEMUBOT v2" + "\n" + "Version :" + VER )
    await channel.send("動作確認されている安定バージョンです")
    await channel.send("============How to use =============" + "\n" +"入力した文字がそのまま送信されます" + "\n" + "なんか操作を受け付けなくなったときは送信したメッセージにつく🔁を押すとCtrl-Cが送信されます")
    await channel.send("default Installed OS : PeckOS" )
    await channel.send("user name : root" +"\n"+"Non Password" )
@client.event
async def on_message(message):
    global qemu_writer
    if message.channel.id != CHANNEL_ID or message.author == client.user:
        return

    if qemu_writer is not None:
        # QEMUへ送信（改行を付ける）
        qemu_writer.write((message.content + "\n").encode())
        await qemu_writer.drain()
        await message.add_reaction("📤")
        await message.add_reaction("🔁")
    
@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if reaction.message.channel.id != CHANNEL_ID:
        return

    # 📤がBot自身によって付けられているか確認
    if any(r.emoji == "📤" and r.me for r in reaction.message.reactions):
        if str(reaction.emoji) == "🔁":
            if qemu_writer:
                    qemu_writer.write(b'\x03')
                    await qemu_writer.drain()
                    channel = client.get_channel(CHANNEL_ID)
                    await channel.send("ソフトリセットを送信しました（Ctrl-C）")



async def read_from_qemu():
    global qemu_writer
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    reader, writer = await asyncio.open_connection(QEMU_HOST, QEMU_PORT)
    qemu_writer = writer
    print("[+] Connected to QEMU")

    buffer = b""
    while not client.is_closed():
        try:
            data = await reader.read(1024)
            if not data:
                await asyncio.sleep(0.001)
                continue
            buffer += data
            if b"\n" in buffer:
                lines = buffer.split(b"\n")
                for line in lines[:-1]:
                    text = line.decode(errors="ignore").strip()
                    if text:
                        await channel.send(f"```{text}```")
                        if DEBUGMODE == True: print(f"[🐛]QEMULog serialLog:{text}")

                buffer = lines[-1]
        except Exception as e:
            print(f"[!] Error reading QEMU: {e}")
            await channel.send(f"[!] Error reading QEMU: {e}")
            await asyncio.sleep(1)


client.run(TOKEN)