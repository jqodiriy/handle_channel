import asyncio
import json
import os.path

from telethon import functions, events
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import PeerUser

import models
from ChannelNewMessage import ChannelNewMessage
from GroupNewMessage import GroupNewMessage

api_id = 20841873
api_hash = '46c1552664380d729eed899cc55f86e1'
phone = 'session_name'
# phone = 'user1234'

FORWARD_FROM_CHANNEL = 1
FORWARD_FROM_USER = 2

loop = asyncio.get_event_loop()

client = TelegramClient(phone, api_id, api_hash, loop=loop)


@client.on(events.NewMessage())
async def handle_new_channel_message(event):
    message = event.message

    if message.post == False:
        newMessage = GroupNewMessage()
        res = await newMessage.toGroupMessage(tg_client=client, message=message)
        print(json.dumps(res))
    else:
        newMessage = ChannelNewMessage()
        result = await newMessage.to_dict(message, client)
        print(json.dumps(result))


class Telethone:
    headers = {'content-type': 'application/json'}
    file_size_limit_MB = 20
    files_url = 'files'
    client: TelegramClient
    profile_photos_limit = 5
    max_post_count = 1000000
    limit = 3
    url = 'http://10.10.110.65:8000/jj/v2/create_many_channel'
    channel_info = None

    def __init__(self):
        with TelegramClient(phone, api_id, api_hash, loop=loop) as tg_client:
            self.client = tg_client

    async def get_channels(self):
        channels = []
        async for dialog in client.iter_dialogs():
            if not dialog.is_group and dialog.is_channel:
                channels.__add__(dialog)
        return channels

    def save_file(self, message, tg_client):
        try:
            if message is None or message.media is None or (message.file.size / 1048576 >= self.file_size_limit_MB):
                return {"file_type": None, "file_dir": None, "file_name": None, "file_id": None, "access_hash": None}

            path = tg_client.download_media(message.media, self.files_url)
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

    async def save_profile_photo(self, username, client):
        photos = []
        count = 0
        async for photo in client.iter_profile_photos(username):
            if count == self.profile_photos_limit:
                break
            count += 1
            path = await client.download_media(photo, self.files_url)
            file_name = str(path)[str(path).index(self.files_url) + len(self.files_url) + 1:]
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

    async def save_user_photo(self, peer_id, tg_client):
        photos = []
        count = 0
        if hasattr(peer_id, 'user_id'):
            result = await tg_client(functions.photos.GetUserPhotosRequest(
                user_id=peer_id.from_id,
                offset=0,
                max_id=0,
                limit=self.profile_photos_limit
            ))
            for photo in result.photos:
                if count == self.profile_photos_limit:
                    break
                count += 1
                path = await tg_client.download_media(photo, self.files_url)
                file_name = str(path)[str(path).index(self.files_url) + len(self.files_url) + 1:]
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

    @staticmethod
    def get_message_reactions(message):
        reactions = []
        for reaction in message.reactions.results:
            r = models.ReactionModel(reaction.reaction.emoticon, reaction.count)
            reactions.append(r.to_dict())
        return reactions if len(reactions) > 0 else None

    def join_channel_request(self, tg_client, channel_name):
        result = tg_client(functions.channels.JoinChannelRequest(
            channel=channel_name
        ))

    def getInfoChannel(self, channel_name):
        channel_data = models.ChannelModel(channel_name)
        self.channel_info = None
        tg_client = self.client
        channel_entity = tg_client.get_entity(channel_name)
        channel_full = tg_client(GetFullChannelRequest(channel=channel_entity))

        try:
            channel_data.profile_photos = loop.run_until_complete(self.save_profile_photo(channel_name, tg_client))
        except Exception as ex:
            print("Exception get photos ", ex)

        channel_data.channel_description = channel_full.full_chat.about
        channel_data.channel_id = channel_entity.id

        channel_data.channel_title = channel_entity.title
        channel_data.channel_username = channel_entity.username
        channel_data.channel_users_count = channel_full.full_chat.participants_count

        if channel_full.chats is not None:
            for chat in channel_full.chats:
                if chat.id != channel_data.channel_id:
                    group = models.GroupModel()
                    group.group_username = chat.username
                    group.group_id = chat.id
                    group.group_title = chat.title
                    group.group_user_count = chat.participants_count

                    try:
                        group_photos = loop.run_until_complete(self.save_profile_photo(channel_name, tg_client))
                        group.photos_dir = group_photos
                    except Exception as ex:
                        print("Exception get photos ", ex)

                    channel_data.channel_group.append(group)

        return channel_data

    def get_comments(self, username: str, message_id: int, tg_client):

        loop = asyncio.get_event_loop()
        discusses = []

        for discuss in tg_client.iter_messages(username, reply_to=message_id):
            discuss_message = models.DiscussModel()
            discuss_message.discuss_date = discuss.date
            discuss_message.message_id = discuss.id
            discuss_message.message_text = discuss.text

            if hasattr(discuss, 'media') and discuss.media is not None:
                media = self.save_file(discuss, tg_client)
                discuss_message.file = media
            if hasattr(discuss, 'from_id') and discuss.from_id is not None:

                if hasattr(discuss.from_id, 'user_id'):
                    discuss_message.user_id = discuss.from_id.user_id

                if hasattr(discuss.from_id, 'channel_id'):
                    discuss_message.channel_id = discuss.from_id.channel_id

            if discuss_message.user_id is not None:
                user = tg_client.get_entity(PeerUser(discuss_message.user_id))
                discuss_message.bot = user.bot
                discuss_message.username = user.username if hasattr(user, 'username') else None
                discuss_message.phone = user.phone if (hasattr(user, 'phone')) else None
                discuss_message.first_name = user.first_name if (
                    hasattr(user, 'first_name')) else None
                discuss_message.second_name = user.last_name if (
                    hasattr(user, 'last_name')) else None
            else:
                continue

            if discuss.reactions is not None:
                discuss_message.reactions = self.get_message_reactions(discuss)
            else:
                discuss_message.reactions = None
            discuss_message.profile_photos = loop.run_until_complete(
                self.save_profile_photo(discuss.from_id, tg_client))

            discusses.append(discuss_message)
        if len(discusses) == 0:
            discusses = None
        return discusses

    def getChannelMessages(self, channel_name):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        with TelegramClient(phone, api_id, api_hash, loop=loop) as tg_client:

            posts = []
            total = 0
            cur_size = 0
            for message_entity in tg_client.iter_messages(channel_name, reverse=False):
                if message_entity.action is not None:
                    continue

                if total == self.max_post_count:
                    self.channel_info.channel_post = posts
                    self.postResult()
                    return

                if cur_size == self.limit:
                    self.channel_info.channel_post = posts
                    self.postResult()
                    posts = []
                    cur_size = 0
                    self.channel_info.channel_post = []

                total += 1
                cur_size += 1

                print(total, cur_size)

                message = models.MessageModel()
                message.channel_id = message_entity.peer_id.channel_id if hasattr(message_entity.peer_id,
                                                                                  'channel_id') else None
                message.post_id = message_entity.id
                message.post_date = message_entity.date
                message.post_text = message_entity.message
                message.pinned = message_entity.pinned
                message.post_view_count = message_entity.views
                message.reply_to_post_id = message_entity.reply_to.reply_to_msg_id if message_entity.reply_to is not None else None
                message.post_owner = message_entity.from_id

                media = self.save_file(message_entity, tg_client)
                message.file = media
                if message_entity.reactions is not None:
                    message.reactions = self.get_message_reactions(message_entity)
                if message_entity.fwd_from is not None:
                    forwarded = message_entity.fwd_from.from_id
                    try:
                        if hasattr(forwarded, 'user_id'):
                            message.forward_type = FORWARD_FROM_USER
                            client_entity = tg_client.get_entity(forwarded.user_id)
                            client_forward = models.ClientModel()
                            client_forward.client_id = client_entity.id
                            client_forward.type = models.ClientType.USER
                            client_forward.username = client_entity.username
                            client_forward.client_name = client_entity.first_name if hasattr(client_entity,
                                                                                             'first_name') else None
                            client_forward.second_name = client_entity.second_name if hasattr(client_entity,
                                                                                              'second_name') else None
                            client_forward.title = client_entity.title if hasattr(client_entity,
                                                                                  'title') else None
                            client_forward.phone = client_entity.phone if hasattr(client_entity, 'phone') else None
                            client_forward.profile_photos = loop.run_until_complete(
                                self.save_profile_photo(message_entity.fwd_from))
                            message.forward_from = client_forward

                        elif hasattr(forwarded, 'channel_id'):
                            message.forward_type = FORWARD_FROM_CHANNEL
                            client_entity = tg_client.get_entity(forwarded.channel_id)
                            client_forward = models.ClientModel()
                            client_forward.from_id = client_entity.id
                            client_forward.type = models.ClientType.CHANNEL
                            client_forward.username = client_entity.username
                            client_forward.client_name = client_entity.first_name if hasattr(client_entity,
                                                                                             'first_name') else None
                            client_forward.title = client_entity.title if hasattr(client_entity,
                                                                                  'title') else None
                            client_forward.phone = client_entity.phone if hasattr(client_entity, 'phone') else None
                            message.forward_from = client_forward

                    except Exception as e:
                        print("forward read error", e)

                try:
                    if hasattr(message_entity, 'replies') and message_entity.replies is not None:
                        message.discussion = self.get_comments(channel_name, message.post_id, tg_client)

                except Exception as e:
                    print("cannot read comments ", e)

                posts.append(message)

            return posts

    async def get_user_by_id(self, user_id):
        with TelegramClient(phone, api_id, api_hash, loop=loop) as tg_client:
            self.client = tg_client

        entity = await tg_client.get_entity(user_id)

    def new_message_handler(self, event):
        message = event.message

    # start the client
    client.start()
    client.run_until_disconnected()

    def scarpe(self, channel_name):
        with TelegramClient(phone, api_id, api_hash, loop=loop) as tg_client:
            self.client = tg_client
            self.join_channel_request(tg_client, channel_name)
            self.channel_info = self.getInfoChannel(channel_name)
            for group in self.channel_info.channel_group:
                self.join_channel_request(tg_client, group.group_id)

            # self.getChannelMessages(channel_name)

    @client.on(events.NewMessage())
    async def handle_new_channel_message(event):
        if hasattr(event.message.peer_id, 'channel_id'):
            event_channel_id = event.message.peer_id.channel_id

    def postResult(self):
        json_result = json.dumps(self.channel_info.to_dict())
        print(json_result)
        # request = requests.post(self.url, json.dumps(self.channel_info.to_dict()), headers=self.headers)
        #
        # if request.status_code != 200:
        #     print('body', json_result)
        #     print('status', request.status_code)


if __name__ == '__main__':
    # with open("channels.csv", 'r') as file:
    #     csvreader = csv.reader(file)
    #     for id, row in enumerate(csvreader):
    #         if id == 0:
    #             continue
    #         print(row[1])
    #         channel = Telethone()
    #         channel.scarpe(row[1])
    telethone = Telethone()
    telethone.scarpe('testchanneltest132')
