from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest

import DownloadFiles
from DownloadFiles import get_profile_photos
from telethone import reactions
from get_forward_info import get_forward_info


class GroupNewMessage:

    async def get_group_info(self, tg_client: TelegramClient, message):
        group = message.peer_id
        group_entity = await tg_client.get_entity(group)
        group_full = await tg_client(GetFullChannelRequest(channel=group_entity))

        group_dict = dict()
        group_dict['group_id'] = group_entity.id
        group_dict['group_title'] = group_entity.title
        group_dict[
            'group_description'] = group_full.full_chat.about if group_full.full_chat is not None and hasattr(
            group_full.full_chat, 'about') else None
        group_dict['username'] = group_entity.username
        group_dict['user_count'] = group_full.full_chat.participants_count
        group_dict['photo'] = await DownloadFiles.get_profile_photos(tg_client, message.peer_id)
        return group_dict

    async def get_message_data(self, tg_client: TelegramClient, message):
        message_data = dict()
        if message.from_id is None:
            message.from_id = message.peer_id
        user_entity = await tg_client.get_entity(message.from_id)

        if hasattr(user_entity, 'channel_id'):
            message_data['channel_id'] = user_entity.channel_id

        if hasattr(user_entity, 'user_id'):
            message_data['user_id'] = user_entity.user_id

        message_data['message_id'] = message.id
        message_data['bot'] = user_entity.bot if hasattr(user_entity, 'bot') else None
        message_data['phone'] = user_entity.phone if hasattr(user_entity, 'phone') else None
        message_data['first_name'] = user_entity.first_name if hasattr(user_entity, 'first_name') else None
        message_data['second_name'] = user_entity.last_name if hasattr(user_entity, 'last_name') else None
        message_data['admin_type'] = 0
        message_data['profile_photos'] = await DownloadFiles.get_profile_photos(tg_client, message.from_id)

        message_data['pinned'] = message.pinned
        message_data['reply_to_message_id'] = message.reply_to.reply_to_msg_id if message.reply_to is not None else None
        message_data['files'] = await DownloadFiles.save_file(tg_client, message)
        message_data['reactions'] = reactions.get_reactions(message)
        message_data['forward_from'] = await get_forward_info(tg_client, message)
        message_data['post'] = dict()

        if message.fwd_from is not None:
            post = dict()
            post['channel_id'] = None

            if hasattr(message.fwd_from, 'channel_post'):
                post['post_id'] = message.fwd_from.channel_post

            if hasattr(message.fwd_from, 'from_id'):
                if hasattr(message.fwd_from.from_id, 'channel_id'):
                    post['channel_id'] = message.fwd_from.from_id.channel_id
            message_data['post'] = post
        return message_data

    async def toGroupMessage(self, tg_client: TelegramClient, message):
        new_message = dict()
        group_data = await self.get_group_info(tg_client, message)
        message_data = await self.get_message_data(tg_client, message)

        new_message['group_data'] = group_data
        new_message['message_data'] = message_data

        return new_message
