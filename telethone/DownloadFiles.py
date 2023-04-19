import os

import cridientals
from cridientals import profile_photos_limit
from cridientals import files_url

from telethon import TelegramClient


def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


async def get_profile_photos(client: TelegramClient, peer_id):
    photos = []
    count = 0
    check_dir(files_url)
    async for photo in client.iter_profile_photos(peer_id):
        if count == profile_photos_limit:
            break
        count += 1
        path = await client.download_media(photo, files_url)
        file_name = str(path)[str(path).index(files_url) + len(files_url) + 1:]
        mim_type = 'image/jpeg' if file_name[0:5] == 'photo' else 'video/mp4'
        data = {
            "file_name": file_name,
            "file_dir": path,
            "file_type": mim_type,
            "file_id": photo.id,
            "access_hash": photo.access_hash
        }
        photos.append(
            data
        )
    return photos if len(photos) > 0 else None


async def save_file(tg_client: TelegramClient, message):
    try:
        if message is None or message.media is None or (message.file.size / 1048576 >= self.file_size_limit_MB):
            return {"file_type": None, "file_dir": None, "file_name": None, "file_id": None, "access_hash": None}

        check_dir(files_url)

        path = tg_client.download_media(message.media, files_url)
        file_name = os.path.basename(path)

        res = {
            "file_type": message.file.mime_type,
            "file_dir": path,
            "file_name": file_name,
            "file_id": message.media.document.id if hasattr(message.media, 'document') else message.media.photo.id,
            "access_hash": message.media.document.access_hash if hasattr(message.media,
                                                                         'document') else message.media.photo.access_hash
        }
        return res
    except Exception as e:
        print("get media error", e)
        return {"file_type": None, "file_dir": None, "file_name": None, "file_id": None, "access_hash": None}
