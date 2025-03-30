import json
from telethon import TelegramClient, events

# Ganti dengan API ID dan API Hash dari my.telegram.org
api_id = 27070252  # Ganti dengan API ID kamu
api_hash = "699eadbbf727532c43922a3ebea93020"  # Ganti dengan API Hash kamu

# Channel sumber (hanya 1)
source_channel = -1002693168185  # Ganti dengan ID channel sumber

# Daftar channel tujuan (bisa lebih dari 1)
destination_channels = [-1002619037206, -4657535678, -1002368857256]  # Tambahkan ID channel tujuan lain

# Buat client Telegram
client = TelegramClient("session_name", api_id, api_hash)

# File untuk menyimpan ID pesan
DATA_FILE = "message_map.json"

# Fungsi untuk menyimpan data pesan
def save_message_map(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

# Fungsi untuk memuat data pesan
def load_message_map():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Muat data pesan yang sudah dikirim
message_map = load_message_map()

@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    global message_map

    try:
        # Simpan pesan sumber
        source_message_id = event.message.id
        message_map.setdefault(str(source_message_id), {})

        # Jika pesan teks
        if event.message.text:
            for destination in destination_channels:
                sent_message = await client.send_message(destination, event.message.text)
                message_map[str(source_message_id)][str(destination)] = sent_message.id

        # Jika pesan media (gambar, video, dll.)
        elif event.message.media:
            for destination in destination_channels:
                sent_message = await client.send_file(destination, event.message.media, caption=event.message.text or "")
                message_map[str(source_message_id)][str(destination)] = sent_message.id

        # Simpan perubahan ke file
        save_message_map(message_map)

    except Exception as e:
        print(f"Error saat mengirim pesan: {e}")

@client.on(events.MessageDeleted(chats=source_channel))
async def delete_handler(event):
    global message_map

    try:
        for message_id in event.deleted_ids:
            if str(message_id) in message_map:
                for destination, dest_msg_id in message_map[str(message_id)].items():
                    await client.delete_messages(int(destination), int(dest_msg_id))
                del message_map[str(message_id)]

        # Simpan perubahan setelah menghapus pesan
        save_message_map(message_map)

    except Exception as e:
        print(f"Error saat menghapus pesan: {e}")

print("Bot sedang berjalan...")
client.start()
client.run_until_disconnected()
