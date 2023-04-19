from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest

import TelegramGroup
import cridientals
from DownloadFiles import get_profile_photos
from DownloadFiles import save_file
from get_forward_info import get_forward_info
from reactions import get_reactions


class ChannelNewMessage:
    profile_photos_limit = cridientals.profile_photos_limit
    files_url = cridientals.files_url

    async def get_channel_info(self, channel, tg_client):
        channel_entity = await tg_client.get_entity(channel)
        channel_full = await tg_client(GetFullChannelRequest(channel=channel_entity))
        res = dict()
        res['channel_id'] = channel_entity.id
        res['channel_title'] = channel_entity.title
        res['channel_username'] = channel_entity.username
        res['channel_users_count'] = channel_full.full_chat.participants_count
        res['channel_description'] = channel_full.full_chat.about
        res['profile_photos'] = await get_profile_photos(tg_client, channel)
        return res

    async def get_chats(self, tg_client: TelegramClient, channel):
        channel_entity = await tg_client.get_entity(channel)
        channel_full = await tg_client(GetFullChannelRequest(channel=channel_entity))
        channels = []
        if channel_full.chats is not None:
            for chat in channel_full.chats:
                if chat.id != channel_entity.id:
                    group_dict = await TelegramGroup.getGroupInfo(tg_client, chat)
                    channels.append(group_dict)
        return channels

    async def get_post(self, tg_client: TelegramClient, message):

        post = dict()
        post['post_id'] = message.id
        post['channel_id'] = message.peer_id.channel_id if hasattr(message.peer_id, 'channel_id') else None
        post['post_text'] = message.message
        post['post_date'] = str(message.date)
        post['post_view_count'] = message.views
        post['pinned'] = message.pinned
        post['reactions'] = get_reactions(message)
        post['reply_to_post_id'] = message.reply_to.reply_to_msg_id if message.reply_to is not None else None
        post['files'] = await save_file(tg_client, message)
        post['forward_from'] = await get_forward_info(tg_client, message)

        return post

    async def to_dict(self, message, tg_client):
        res = dict()
        channel = await self.get_channel_info(message.peer_id, tg_client)
        groups = await self.get_chats(tg_client, message.peer_id)
        res['channel_id'] = channel['channel_id']
        res['channel_title'] = channel['channel_title']
        res['channel_username'] = channel['channel_username']
        res['channel_users_count'] = channel['channel_users_count']
        res['channel_description'] = channel['channel_description']
        res['profile_photos'] = channel['profile_photos']
        res['channel_group'] = groups
        res['channel_post'] = []

        post = await self.get_post(tg_client, message)
        res['channel_post'].append(post)
        return res
