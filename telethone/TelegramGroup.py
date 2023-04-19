from telethon import TelegramClient
from DownloadFiles import get_profile_photos


async def getGroupInfo(tg_client: TelegramClient, group):
    group_dict = dict()
    group_dict['group_id'] = group.id
    group_dict['group_username'] = group.username
    group_dict['group_title'] = group.title
    group_dict['group_user_count'] = group.participants_count

    try:
        group_photos = await get_profile_photos(tg_client, group)
        group_dict['photos_dir'] = group_photos
    except Exception as ex:
        print("Exception get photos ", ex)
    return group_dict
