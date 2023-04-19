from telethone import models


def get_reactions(message):
    reactions = []
    if message.reactions is not None:
        for reaction in message.reactions.results:
            r = dict()
            r['emotion'] = reaction.reaction.emoticon
            r['count'] = reaction.count
            reactions.append(r)
    if len(reactions) == 0:
        reactions = None
    return reactions
