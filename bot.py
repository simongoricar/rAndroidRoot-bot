import logging
logging.basicConfig(level=logging.INFO)

from typing import Optional
from random import choice
from asyncio import TimeoutError

from discord import Member, Guild, TextChannel, Message, PermissionOverwrite, Role, CategoryChannel
from discord.ext.commands import Bot, Context
from discord import RawReactionActionEvent

from androidroot.state import state
from androidroot.config import BOT_TOKEN, GUILD_ID, \
    AUTH_TRIGGER_CHANNEL_ID, AUTH_TRIGGER_MESSAGE_ID, AUTH_TRIGGER_EMOJI,\
    AUTH_CHANNEL_CATEGORY_ID, AUTH_SUCCESS_ROLE_ID
from androidroot.strings import STR_ON_MEMBER_JOIN, ON_VERIFICATION_BEGIN, \
    VERIFICATION_HOW, VERIFY_NOT_BOT_TEXT_LIST, VERIFY_RANDOM_EMOJI_LIST,\
    VERIFY_FAILED_TIMEOUT, VERIFY_SUCCESS, BOT_ABOUT
from androidroot.utilities import generate_id

__version__ = "0.1.0"

log = logging.getLogger(__name__)
bot = Bot(
    command_prefix="!"
)


#############
# Helper code
#############

# These functions cache the Guild, TextChannel and Message objects
async def get_main_guild() -> Guild:
    """
    :return: Guild that was configured for this bot to work on
    """
    stored: Optional[Guild] = state.get("main_guild")

    if stored is None:
        main_guild = bot.get_guild(GUILD_ID)
        state.set("main_guild", main_guild)
        return main_guild
    else:
        return stored


async def get_auth_channel() -> TextChannel:
    """
    :return: Verification TextChannel
    """
    stored: Optional[TextChannel] = state.get("auth_channel")

    if stored is None:
        auth_channel = (await get_main_guild()).get_channel(AUTH_TRIGGER_CHANNEL_ID)
        state.set("auth_channel", auth_channel)
        return auth_channel
    else:
        return stored


async def get_auth_trigger_message() -> Message:
    """
    :return: Verification trigger Message
    """
    stored: Optional[Message] = state.get("auth_trigger_message")

    if stored is None:
        trigger_message = await (await get_auth_channel()).fetch_message(AUTH_TRIGGER_MESSAGE_ID)
        state.set("auth_trigger_message", trigger_message)
        return trigger_message
    else:
        return stored


async def get_auth_success_role() -> Role:
    """
    :return: Role to add when successfully authenticated.
    """
    stored: Optional[Role] = state.get("auth_success_role")

    if stored is None:
        success_role = (await get_main_guild()).get_role(AUTH_SUCCESS_ROLE_ID)
        state.set("auth_success_role", success_role)
        return success_role
    else:
        return stored


def find_category_by_id(guild: Guild, category_id: int) -> Optional[CategoryChannel]:
    category = None
    for c in guild.categories:
        if c.id == category_id:
            category = c
            break

    return category


#############
# Verification code
#############
async def begin_verification(member: Member):
    main_guild = await get_main_guild()

    # Create new channel
    channel_name = f"verification-{generate_id(4)}"

    # Find the correct category
    category = find_category_by_id(main_guild, AUTH_CHANNEL_CATEGORY_ID)
    if not category:
        raise Exception(f"Could not find category with ID {AUTH_CHANNEL_CATEGORY_ID}")

    permission_overwrites = {
        main_guild.me: PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True),
        member: PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True),
        main_guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False)
    }

    auth_channel = await main_guild.create_text_channel(
        channel_name,
        category=category,
        overwrites=permission_overwrites,
        reason=f"Authenticating user {member.id}#{member.discriminator}"
    )

    random_not_bot_text = choice(VERIFY_NOT_BOT_TEXT_LIST)
    random_emoji = choice(VERIFY_RANDOM_EMOJI_LIST)

    await auth_channel.send(ON_VERIFICATION_BEGIN.format(user_mention=member.mention))
    await auth_channel.send(VERIFICATION_HOW.format(
        not_bot_text=random_not_bot_text,
        random_emoji=random_emoji,
    ))

    try:
        def is_correct_response(message: Message):
            if message.author.id != member.id:
                return False
            if message.channel.id != auth_channel.id:
                return False

            if random_not_bot_text not in str(message.content):
                return False
            if random_emoji not in str(message.content):
                return False

            return True

        response: Message = await bot.wait_for("message", check=is_correct_response, timeout=120)
    except TimeoutError:
        # Tell the user they were too slow and delete the verification channel
        await member.send(VERIFY_FAILED_TIMEOUT)
        await auth_channel.delete(reason=f"Verification for {member.name}#{member.discriminator} ({member.id}) "
                                         f"failed: timeout")
    else:
        await response.add_reaction("✅")

        # Assign the full member role
        full_role = await get_auth_success_role()
        await member.add_roles(full_role, reason=f"Verification finished")

        await member.send(VERIFY_SUCCESS.format(user_mention=member.mention))
        await auth_channel.delete(reason=f"Verification for {member.name}#{member.discriminator} ({member.id}) "
                                         f"finished")


#############
# Discord events
#############
@bot.listen()
async def on_ready():
    log.info(f"Bot is ready: logged in as {bot.user.name} ({bot.user.id})")

    # Really make sure the internal cache is ready
    await bot.wait_until_ready()

    # Delete all stale verification channels on start
    auth_category = find_category_by_id(await get_main_guild(), AUTH_CHANNEL_CATEGORY_ID)
    if not auth_category:
        raise Exception(f"Could not find category with ID {AUTH_CHANNEL_CATEGORY_ID}")

    for ch in auth_category.text_channels:
        # Make sure they match verification-<4digits>
        if len(ch.name) != len("verification-1234"):
            return
        if not str(ch.name).startswith("verification-"):
            return

        log.warning(f"Deleting stale verification channel: {ch.name} ({ch.id})")
        await ch.delete(reason="Cleaning stale verification channels on start.")

    # Puts up the first reaction on the trigger message
    trigger_message = await get_auth_trigger_message()
    await trigger_message.add_reaction(AUTH_TRIGGER_EMOJI)


@bot.listen()
async def on_member_join(member: Member):
    # Send a DM instructing the member to get verified
    auth_channel = await get_auth_channel()

    formatted = STR_ON_MEMBER_JOIN.format(user_mention=member.mention, channel_mention=auth_channel.mention)
    await member.send(formatted)


@bot.listen()
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    if payload.member.bot:
        return

    # Check if it matches with the correct message
    if payload.message_id != AUTH_TRIGGER_MESSAGE_ID:
        return

    # Check if the emoji is correct
    if str(payload.emoji) != AUTH_TRIGGER_EMOJI:
        return

    # Check if user is already authenticated
    full_role = await get_auth_success_role()
    if full_role in payload.member.roles:
        log.debug(f"User {payload.member.name}#{payload.member.discriminator} "
                  f"is already authenticated, ignoring reaction.")
        return

    # Begin the verification
    log.info(f"Got new verification request: user {payload.user_id}")
    await begin_verification(payload.member)


#############
# Bot commands
#############
@bot.command(name="ping")
async def cmd_ping(ctx: Context):
    await ctx.send("Pong! :ping_pong:")


@bot.command(name="about")
async def cmd_about(ctx: Context):
    await ctx.send(BOT_ABOUT.format(bot_mention=bot.user.mention, bot_version=__version__))

# Run everything
bot.run(BOT_TOKEN)
