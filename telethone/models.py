import enum
import json


class ChannelModel:
    channel_id = None
    channel_username = None
    channel_title = None
    channel_description = None
    channel_users_count = None

    channel_post = None
    profile_photos = []
    channel_group = []

    def __init__(self, name):
        self.channel_title = name

    def __str__(self):
        return f"""
            channel_id -> {self.channel_id}, 
            username -> {self.channel_username},
            title -> {self.channel_title},
            description -> {self.channel_description},
            users_count -> {self.channel_users_count},
            photo_dir -> {self.profile_photos}, 
            messages -> {self.channel_post}
            chats -> ${self.channel_group}
        """

    def to_dict(self):
        channel_dict = dict()
        channel_dict['channel_id'] = self.channel_id
        channel_dict['channel_username'] = self.channel_username
        channel_dict['channel_description'] = self.channel_description
        channel_dict['channel_users_count'] = self.channel_users_count
        channel_dict['profile_photos'] = self.profile_photos if self.profile_photos is not None and len(
            self.profile_photos) > 0 else None
        channel_dict['channel_title'] = self.channel_title
        channel_dict['channel_group'] = None if self.channel_group is None or len(self.channel_group) == 0 else []
        channel_dict['channel_post'] = None if self.channel_post is None or len(self.channel_post) == 0 else []

        if self.channel_group is not None and len(self.channel_group) > 0:
            for gr in self.channel_group:
                channel_dict['channel_group'].append(gr.to_dict())

        if self.channel_post is not None and len(self.channel_post) > 0:
            for post in self.channel_post:
                channel_dict['channel_post'].append(post.to_dict())
        return channel_dict

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class GroupModel:
    group_id = None
    group_username = None
    group_title = None
    group_description = None
    group_user_count = None
    photos_dir = []

    def __str__(self):
        return f"""
               group_id -> {self.group_id}, 
               group_username -> {self.group_username},
               title -> {self.group_title},
               users_count -> {self.group_user_count},
               photo_dir -> {self.photos_dir}
           """

    def to_dict(self):
        group_dict = dict()
        group_dict['group_id'] = self.group_id
        group_dict['group_username'] = self.group_username
        group_dict['group_title'] = self.group_title
        group_dict['group_description'] = self.group_description
        group_dict['group_users_count'] = self.group_user_count
        group_dict['photos_dir'] = self.photos_dir if self.photos_dir is not None and len(self.photos_dir) > 0 else None

        return group_dict


class MessageModel:
    post_id = 0
    channel_id = 0
    post_text = ''
    post_date = None
    post_edit_date = None
    file = None
    post_view_count = None
    forward_from = None
    pinned = False
    reactions = None
    reply_to_post_id = None
    discussion = []
    post_owner = None

    def __init__(self):
        self.post_id = -1
        self.message_reactions = []

    def __str__(self):
        reactions_str = '['
        for r in self.message_reactions:
            reactions_str += str(r) + ';\n'
        reactions_str += ']'

        res = f"""
            message_id:     {self.post_id},
            channel_id:     {self.channel_id},
            message_text:   {self.post_text},
            media:     {self.file},
            message_date:   {self.post_date},
            message_view_count: {self.post_view_count},
            forward from : {self.forward_from},
            message_pinned: {self.pinned},
            reactions: {reactions_str}
            """
        return res

    def to_dict(self):
        message_dic = dict()
        message_dic['post_id'] = self.post_id
        message_dic['channel_id'] = self.channel_id
        message_dic["post_text"] = self.post_text
        message_dic['files'] = self.file
        message_dic['post_date'] = str(self.post_date)
        message_dic['post_edit_date'] = self.post_edit_date
        message_dic['post_view_count'] = self.post_view_count
        message_dic['forward_from'] = self.forward_from.to_dict() if self.forward_from is not None else None
        message_dic['pinned'] = self.pinned
        message_dic['reactions'] = self.reactions
        message_dic['reply_to_post_id'] = self.reply_to_post_id
        message_dic['discussion'] = []
        if self.forward_from is not None:
            message_dic["forward_from"] = self.forward_from.to_dict()


        if self.discussion is not None:
            for d in self.discussion:
                message_dic['discussion'].append(d.to_dict())

        if message_dic['discussion'] is None or len(message_dic['discussion']) == 0:
            message_dic['discussion'] = None

        return message_dic

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class ReactionModel:
    emotion = ''
    count = 0

    def __init__(self, emotion, count):
        self.emotion = emotion
        self.count = count

    def __str__(self):
        return f"icon {self.emotion} , count {self.count} "

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_dict(self):
        reaction_dict = dict()
        reaction_dict["emotion"] = self.emotion
        reaction_dict["count"] = self.count
        return reaction_dict


class ClientType(enum.Enum):
    USER = 1
    CHANNEL = 2
    GROUP = 3
    BOT = 4


class ClientModel:
    type = ClientType.USER
    profile_photos = None
    from_id = None
    group_id = None
    description = None
    title = None
    username = None
    second_name = None
    first_name = None
    phone = None

    def to_dict(self):
        client_dict = dict()
        client_dict["type"] = self.type.value
        client_dict["from_id"] = self.from_id
        client_dict["username"] = self.username
        client_dict["first_name"] = self.first_name
        client_dict["second_name"] = self.second_name
        client_dict["description"] = self.description
        client_dict["title"] = self.title
        client_dict["phone"] = self.phone
        client_dict['profile_photos'] = self.profile_photos
        return client_dict


class FileModel:
    file_type = None
    file_dir = None
    file_name = None
    file_id = None
    access_hash = None

    def __init__(self):
        self.file_type = 0

    def __str__(self):
        f"""file_type = ${self.file_type},
        file_dir = ${self.file_dir},
        file_name = ${self.file_name}"""

    def to_dict(self):
        res = dict()
        res['file_type'] = self.file_type
        res['file_dir'] = self.file_dir
        res['file_name'] = self.file_name
        return res


class DiscussModel:
    user_id = None
    discuss_date = None
    channel_id = None
    message_id = None
    username = None
    first_name = None
    second_name = None
    phone = None
    bot = False
    admin_type = 0
    file = None
    message_text = None
    pinned = False
    reactions = []
    reply_to_msg_id = None
    profile_photos = []

    def to_dict(self):
        res = dict()
        res['user_id'] = self.user_id
        res['message_id'] = self.message_id
        res['username'] = self.username
        res['first_name'] = self.first_name
        res['second_name'] = self.second_name
        res['phone'] = self.phone
        res['discuss_date'] = str(self.discuss_date)
        res['message_text'] = self.message_text
        res['pinned'] = self.pinned
        res['reply_to_msg_id'] = self.reply_to_msg_id
        res['files'] = self.file
        res['reactions'] = self.reactions
        res['bot'] = self.bot
        res['profile_photos'] = self.profile_photos
        return res
