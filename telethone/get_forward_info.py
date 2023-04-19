from telethon import TelegramClient


async def get_forward_info(tg_client: TelegramClient, message):
    forward_from = dict()
    if message.fwd_from is not None:
        fwd_from = None
        if message.fwd_from is not None and hasattr(message.fwd_from,
                                                    'from_id') and message.fwd_from.from_id is not None:
            fwd_from = await tg_client.get_entity(message.fwd_from.from_id)

        if fwd_from is not None and hasattr(fwd_from, 'username'):
            forward_from['username'] = fwd_from.username

        if message.fwd_from.from_id is not None:
            if hasattr(message.fwd_from.from_id, 'channel_id'):
                forward_from['type'] = 2
                forward_from['from_id'] = message.fwd_from.from_id.channel_id
            else:
                forward_from['type'] = 1
                forward_from['from_id'] = message.fwd_from.from_id.user_id
        forward_from['first_name'] = fwd_from.first_name if hasattr(fwd_from, 'first_name') else None
        forward_from['second_name'] = fwd_from.last_name if hasattr(fwd_from, 'last_name') else None
        forward_from['phone'] = fwd_from.phone if hasattr(fwd_from, 'phone') else None
    else:
        forward_from = None
    return forward_from
