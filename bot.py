import logging
logging.basicConfig(level=logging.INFO)

from typing import Optional
from discord import AutoShardedClient, Member, Guild, TextChannel, Message

from androidroot.state import state
from androidroot.config import BOT_TOKEN, GUILD_ID, AUTH_TRIGGER_CHANNEL_ID, AUTH_TRIGGER_MESSAGE_ID
from androidroot.strings import STR_ON_MEMBER_JOIN

log = logging.getLogger(__name__)
client = AutoShardedClient()


#############
# Helper code
#############
async def get_main_guild() -> Guild:
    stored: Optional[Guild] = state.get("main_guild")

    if stored is None:
        main_guild = client.get_guild(GUILD_ID)
        state.set("main_guild", main_guild)
        return main_guild
    else:
        return stored


async def get_auth_channel() -> TextChannel:
    stored: Optional[TextChannel] = state.get("auth_channel")

    if stored is None:
        auth_channel = (await get_main_guild()).get_channel(AUTH_TRIGGER_CHANNEL_ID)
        state.set("auth_channel", auth_channel)
        return auth_channel
    else:
        return stored


async def get_auth_trigger_message() -> Message:
    stored: Optional[Message] = state.get("auth_trigger_message")

    if stored is None:
        trigger_message = (await get_auth_channel()).fetch_message(AUTH_TRIGGER_MESSAGE_ID)
        state.set("auth_trigger_message", trigger_message)
        return trigger_message
    else:
        return stored


#############
# Discord events
#############
@client.event
async def on_ready():
    log.info(f"Bot is ready: logged in as {client.user.name} ({client.user.id})")

    # Really make sure the internal cache is ready
    await client.wait_until_ready()

    # Caches the main guild, auth channel and trigger message for subsequent calls for performance
    await get_auth_trigger_message()


@client.event
async def on_member_join(member: Member):
    # Send a DM instructing the member to get verified
    auth_channel = await get_auth_channel()

    formatted = STR_ON_MEMBER_JOIN.format(user_mention=member.mention, channel_mention=auth_channel.mention)
    await member.send(formatted)


# Run everything
client.run(BOT_TOKEN)
