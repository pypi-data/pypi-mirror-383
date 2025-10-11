from re import search

from discord import Embed, Message
from discord.ext import commands

from pycordViews import EasyModifiedViews

from .utils.utils_message import utils_get_message, utils_autorised_mentions
from .._utils import NoneType

__all__ = [
    'dshell_send_message',
    'dshell_respond_message',
    'dshell_delete_message',
    'dshell_purge_message',
    'dshell_edit_message',
    'dshell_get_history_messages',
    'dshell_add_reactions',
    'dshell_remove_reactions',
    'dshell_clear_message_reactions',
    'dshell_clear_one_reactions',
    'dshell_get_content_message'
]


async def dshell_send_message(ctx: Message,
                              message=None,
                              delete=None,
                              channel=None,
                              global_mentions: bool = None,
                              everyone_mention: bool = True,
                              roles_mentions: bool = True,
                              users_mentions: bool = True,
                              reply_mention: bool = False,
                              embeds=None,
                              view=None) -> int:
    """
    Sends a message on Discord
    """

    if delete is not None and not isinstance(delete, (int, float)):
        raise Exception(f'Delete parameter must be a number (seconds) or None, not {type(delete)} !')

    channel_to_send = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)
    allowed_mentions = utils_autorised_mentions(global_mentions, everyone_mention, roles_mentions, users_mentions, reply_mention)

    if channel_to_send is None:
        raise Exception(f'Channel {channel} not found!')

    from .._DshellParser.ast_nodes import ListNode

    if not isinstance(embeds, (ListNode, Embed, NoneType)):
        raise Exception(f'Embeds must be a list of Embed objects or a single Embed object, not {type(embeds)} !')

    if embeds is None:
        embeds = ListNode([])

    elif isinstance(embeds, Embed):
        embeds = ListNode([embeds])

    if not isinstance(view, (EasyModifiedViews, NoneType)):
        raise Exception(f'Channel must be an UI or None, not {type(channel_to_send)} !')

    sended_message = await channel_to_send.send(message,
                                                delete_after=delete,
                                                embeds=embeds,
                                                allowed_mentions=allowed_mentions,
                                                view=view)

    return sended_message.id


async def dshell_respond_message(ctx: Message,
                                 message=None,
                                 content: str = None,
                                 global_mentions: bool = None,
                                 everyone_mention: bool = True,
                                 roles_mentions: bool = True,
                                 users_mentions: bool = True,
                                 reply_mention: bool = False,
                                 delete=None,
                                 embeds=None):
    """
    Responds to a message on Discord
    """
    if delete is not None and not isinstance(delete, (int, float)):
        raise Exception(f'Delete parameter must be a number (seconds) or None, not {type(delete)} !')

    respond_message = ctx if message is None else utils_get_message(ctx, message)  # builds a reference to the message (even if it doesn't exist)
    autorised_mentions = utils_autorised_mentions(global_mentions, everyone_mention, roles_mentions, users_mentions, reply_mention)
    mention_author = True if reply_mention else False

    from .._DshellParser.ast_nodes import ListNode

    if not isinstance(embeds, (ListNode, Embed, NoneType)):
        raise Exception(f'Embeds must be a list of Embed objects or a single Embed object, not {type(embeds)} !')

    if embeds is None:
        embeds = ListNode([])

    elif isinstance(embeds, Embed):
        embeds = ListNode([embeds])

    sended_message = await respond_message.reply(
                                     content=str(content),
                                     mention_author=mention_author,
                                     allowed_mentions=autorised_mentions,
                                     delete_after=delete,
                                     embeds=embeds)

    return sended_message.id

async def dshell_delete_message(ctx: Message, message=None, reason=None, delay=0):
    """
    Deletes a message
    """

    delete_message = ctx if message is None else utils_get_message(ctx, message)

    if not isinstance(delay, int):
        raise Exception(f'Delete delay must be an integer, not {type(delay)} !')

    if delay > 3600:
        raise Exception(f'The message deletion delay is too long! ({delay} seconds)')

    await delete_message.delete(delay=delay, reason=reason)


async def dshell_purge_message(ctx: Message, message_number: int, channel=None, reason=None):
    """
    Purges messages from a channel
    """

    if not isinstance(message_number, int):
        raise Exception(f'Message number must be an integer, not {type(message_number)} !')

    purge_channel = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if purge_channel is None:
        raise Exception(f"Channel {channel} to purge not found!")

    await purge_channel.purge(limit=message_number, reason=reason)


async def dshell_edit_message(ctx: Message, message, new_content=None, embeds=None, view=None) -> int:
    """
    Edits a message
    """
    edit_message = utils_get_message(ctx, message)

    from .._DshellParser.ast_nodes import ListNode

    if not isinstance(embeds, (ListNode, Embed, NoneType)):
        raise Exception(f'Embeds must be a list of Embed objects or a single Embed object, not {type(embeds)} !')

    if not isinstance(view, (EasyModifiedViews, NoneType)):
        raise Exception(f'View must be an UI bloc or None, not {type(view)} !')

    if embeds is None:
        embeds = ListNode([])

    elif isinstance(embeds, Embed):
        embeds = ListNode([embeds])

    await edit_message.edit(content=new_content, embeds=embeds, view=view)

    return edit_message.id


async def dshell_get_history_messages(ctx: Message, channel=None, limit=None) -> "ListNode":
    """
    Searches for messages matching a regex in a channel
    """

    if limit is not None and not isinstance(limit, int):
        raise Exception(f"Limit must be an integer or None, not {type(limit)}!")

    search_channel = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if search_channel is None:
        raise Exception(f"Channel {channel} to search not found!")

    from .._DshellParser.ast_nodes import ListNode

    messages = ListNode([])
    async for message in search_channel.history(limit=limit):
        messages.add(message.id)

    if not messages:
        raise commands.CommandError(f"No messages in {search_channel.mention}.")

    return messages



async def dshell_add_reactions(ctx: Message, reactions, message=None):
    """
    Adds reactions to a message
    """
    message = ctx if message is None else utils_get_message(ctx, message)

    if isinstance(reactions, str):
        reactions = (reactions,)

    for reaction in reactions:
        await message.add_reaction(reaction)

    return message.id


async def dshell_remove_reactions(ctx: Message, reactions, message=None):
    """
    Removes reactions from a message
    """
    message = ctx if message is None else utils_get_message(ctx, message)

    if isinstance(reactions, str):
        reactions = [reactions]

    for reaction in reactions:
        await message.clear_reaction(reaction)

    return message.id

async def dshell_clear_message_reactions(ctx: Message, message):
    """
    Clear all reaction on the target message
    """
    message = ctx if message is None else utils_get_message(ctx, message)

    if message is None:
        raise Exception(f'Message not found !')

    await message.clear_reactions()

async def dshell_clear_one_reactions(ctx: Message, message, emoji):
    """
    Clear one emoji on the target message
    """

    if not isinstance(emoji, str):
        raise Exception(f'Emoji must be string, not {type(emoji)}')

    target_message = ctx if message is None else utils_get_message(ctx, message)

    await target_message.clear_reaction(emoji)

async def dshell_get_content_message(ctx: Message, message=None):
    """
    Get the content of a message
    """

    target_message = ctx if message is None else utils_get_message(ctx, message)

    try:
        fetch_target_message = await target_message.fetch()
    except:
        raise Exception(f'Message not found !')

    return fetch_target_message.content


