import logging
logging.basicConfig(level=logging.INFO)

from typing import Optional
from random import choice
from asyncio import TimeoutError
from datetime import datetime

from discord import Member, Guild, TextChannel, Message, PermissionOverwrite, Role, \
    CategoryChannel, Reaction, Embed, Color, Client
from discord.ext.commands import Bot, Context, check_any, CheckFailure
from discord import RawReactionActionEvent
from discord.errors import HTTPException

from androidroot.state import state
from androidroot.config import BOT_TOKEN, BOT_PREFIX, GUILD_ID, \
    VERIFICATION_TRIGGER_CHANNEL_ID, VERIFICATION_TRIGGER_MESSAGE_ID, VERIFICATION_TRIGGER_EMOJI, \
    VERIFICATION_CHANNEL_CATEGORY_ID, VERIFICATION_SUCCESS_ROLE_ID, \
    LOG_VERIFICATIONS_CONSOLE, LOG_VERIFICATIONS_CHANNEL, \
    DISCORD_STATUS_NAME_NAME, DISCORD_TYPE, \
    DISCORD_TWITCH
from androidroot.strings import gets, String
from androidroot.utilities import generate_id, generate_code
from androidroot.checks import is_server_owner, is_special_user, decorate_check
from androidroot.emoji import StandardEmoji, UnicodeEmoji
import sys
import discord
client = discord.Client()

__version__ = "0.3.0"

log = logging.getLogger(__name__)
bot = Bot(
    command_prefix=BOT_PREFIX
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


async def get_verify_trigger_channel() -> TextChannel:
    """
    :return: Verification TextChannel
    """
    stored: Optional[TextChannel] = state.get("auth_channel")

    if stored is None:
        auth_channel = (await get_main_guild()).get_channel(VERIFICATION_TRIGGER_CHANNEL_ID)
        state.set("auth_channel", auth_channel)
        return auth_channel
    else:
        return stored


async def get_verify_trigger_message() -> Message:
    """
    :return: Verification trigger Message
    """
    stored: Optional[Message] = state.get("auth_trigger_message")

    if stored is None:
        trigger_message = await (await get_verify_trigger_channel()).fetch_message(VERIFICATION_TRIGGER_MESSAGE_ID)
        state.set("auth_trigger_message", trigger_message)
        return trigger_message
    else:
        return stored


async def get_verified_role() -> Role:
    """
    :return: Role to add when successfully authenticated.
    """
    stored: Optional[Role] = state.get("auth_success_role")

    if stored is None:
        success_role = (await get_main_guild()).get_role(VERIFICATION_SUCCESS_ROLE_ID)
        state.set("auth_success_role", success_role)
        return success_role
    else:
        return stored


# TODO use decorators for caching instead of doing it manually in each function
async def get_logging_channel() -> Optional[TextChannel]:
    """
    :return: Verification logging channel
    """
    if LOG_VERIFICATIONS_CHANNEL is None:
        return None

    stored: Optional[TextChannel] = state.get("verification_logging_channel")

    if stored is None:
        logging_channel = (await get_main_guild()).get_channel(LOG_VERIFICATIONS_CHANNEL)
        state.set("verification_logging_channel", logging_channel)
        return logging_channel
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
    category = find_category_by_id(main_guild, VERIFICATION_CHANNEL_CATEGORY_ID)
    if not category:
        raise Exception(f"Could not find category with ID {VERIFICATION_CHANNEL_CATEGORY_ID}")

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

    random_code = generate_code(4)
    random_emoji_text, random_emoji_unicode = choice(gets(String.VERIFY_RANDOM_EMOJI_LIST))

    await auth_channel.send(gets(String.ON_VERIFICATION_BEGIN).format(user_mention=member.mention))
    await auth_channel.send(gets(String.VERIFICATION_HOW).format(
        code=random_code,
        random_emoji=random_emoji_text.strip(":"),
    ))

    responses = []
    embed = None

    try:
        failed_tries = 0

        def is_correct_response(message: Message):
            if message.author.id != member.id:
                return False
            if message.channel.id != auth_channel.id:
                return False

            responses.append(message)

            content = str(message.content).strip().lower()
            # Should begin with the code and end with the emoji
            if random_code.lower() not in content:
                return False
            if random_emoji_unicode not in content:
                return False

            return True

        response: Message = await bot.wait_for("message", check=is_correct_response, timeout=120)
    except TimeoutError:
        # Tell the user they were too slow and delete the verification channel
        await member.send(gets(String.VERIFY_FAILED_TIMEOUT))
        await auth_channel.delete(reason=f"Verification for {member.name}#{member.discriminator} ({member.id}) "
                                         f"failed: timeout")

        if len(responses) == 0:
            if LOG_VERIFICATIONS_CONSOLE:
                log.info(f"Member failed to verify (timeout): {member.name}#{member.discriminator} ({member.id}), "
                         f"expected '{random_code} {random_emoji_unicode}', no responses")

            embed = Embed(
                title="User failed to verify (timeout)",
                description=f"*Expected \"{random_code} {random_emoji_unicode}\"*\n"
                            f"*No response*", color=Color.dark_red(),
                timestamp=datetime.now()
            )
        else:
            last_message = responses[-1]

            trimmed = last_message.clean_content
            if len(trimmed) > 1000:
                trimmed = f"{trimmed[:1000]}[...]"

            if LOG_VERIFICATIONS_CONSOLE:
                log.info(f"Member not verified (timeout): {member.name}#{member.discriminator} ({member.id}), "
                         f"expected '{random_code} {random_emoji_unicode}', last response '{trimmed}'")

            embed = Embed(
                title="Member failed to verify (timeout)",
                description=f"*Expected \"{random_code} {random_emoji_unicode}\"*\n"
                            f"Last response:\n```{trimmed}```", color=Color.red(),
                timestamp=datetime.now()
            )
    else:
        await response.add_reaction("✅")

        # Assign the full member role
        full_role = await get_verified_role()
        await member.add_roles(full_role, reason=f"Verification finished")

        await member.send(gets(String.VERIFY_SUCCESS).format(user_mention=member.mention))
        await auth_channel.delete(reason=f"Verification for {member.name}#{member.discriminator} ({member.id}) "
                                         f"finished")

        trimmed = response.clean_content
        if len(trimmed) > 1000:
            trimmed = f"{trimmed[:1000]}[...]"

        if LOG_VERIFICATIONS_CONSOLE:
            log.info(f"Member verified: {member.name}#{member.discriminator} ({member.id}) with message '{trimmed}' "
                     f"(expected \"{random_code} {random_emoji_unicode}\")")

        embed = Embed(
            title="Member verified",
            description=f"*Expected \"{random_code} {random_emoji_unicode}\"*\n"
                        f"```{trimmed}```", color=Color.green(),
            timestamp=datetime.now()
        )
    finally:
        # Remove the reaction on the main message
        trigger_messsage = await get_verify_trigger_message()
        await trigger_messsage.remove_reaction(VERIFICATION_TRIGGER_EMOJI, member)

        # Send the log embed if enabled
        log_channel = await get_logging_channel()
        if log_channel is not None:
            embed.set_footer(
                text=f"Member: {member.name}#{member.discriminator} ({member.id})",
                icon_url=member.avatar_url
            )

            await log_channel.send(embed=embed)


#############
# Discord events
#############
@bot.listen()
async def on_ready():
    # badly implement status lmao

    if(DISCORD_TYPE == "watching"):
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=DISCORD_STATUS_NAME))

    elif(DISCORD_TYPE == "playing"):
        await bot.change_presence(activity=discord.Game(name=DISCORD_STATUS_NAME))

    elif(DISCORD_TYPE == "listening"):
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=DISCORD_STATUS_NAME))

    elif(DISCORD_TYPE == "streaming"):
        change_presence(activity=discord.Streaming(name=DISCORD_STATUS_NAME, url=DISCORD_TWITCH))

    log.info("Bot is ready: logged in as {bot.user.name} ({bot.user.id})")
    log.info("Checking for Pterodactyl...")
    pterotest = str(sys.argv)
    if(pterotest[1] == "ptero"):
        print("Pterodactyl Detected!")
    else:
        print("Pterodactyl not found.")

    # Really make sure the internal cache is ready
    await bot.wait_until_ready()

    # Delete all stale verification channels on start
    auth_category = find_category_by_id(await get_main_guild(), VERIFICATION_CHANNEL_CATEGORY_ID)
    if not auth_category:
        raise Exception(f"Could not find category with ID {VERIFICATION_CHANNEL_CATEGORY_ID}")

    for ch in auth_category.text_channels:
        # Make sure they match verification-<4digits>
        if len(ch.name) != len("verification-1234"):
            return
        if not str(ch.name).startswith("verification-"):
            return

        log.warning(f"Deleting stale verification channel: {ch.name} ({ch.id})")
        await ch.delete(reason="Cleaning stale verification channels on start.")

    # Puts up the first reaction on the trigger message
    trigger_message = await get_verify_trigger_message()
    await trigger_message.add_reaction(VERIFICATION_TRIGGER_EMOJI)


@bot.listen()
async def on_member_join(member: Member):
    # Send a DM instructing the member to get verified
    auth_channel = await get_verify_trigger_channel()

    formatted = gets(String.ON_MEMBER_JOIN).format(user_mention=member.mention, channel_mention=auth_channel.mention)
    await member.send(formatted)


@bot.listen()
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    # Ignore all "official" bots
    if payload.member.bot:
        return

    # Check if it matches with the correct message
    if payload.message_id != VERIFICATION_TRIGGER_MESSAGE_ID:
        return

    # Check if the emoji is correct
    if str(payload.emoji) != VERIFICATION_TRIGGER_EMOJI:
        return

    # Check if user is already authenticated
    full_role = await get_verified_role()
    if full_role in payload.member.roles:
        log.debug(f"User {payload.member.name}#{payload.member.discriminator} "
                  f"is already authenticated, ignoring reaction.")
        return

    # Begin the verification
    log.info(f"Got new verification request: user {payload.user_id}")
    await begin_verification(payload.member)


#############
# Dangerous commands
#############
@check_any(decorate_check(is_server_owner), decorate_check(is_special_user))
@bot.command(name="verifyall", brief="Give every member the verified role (owner only)")
async def cmd_verifyall(ctx: Context):
    verified_role = await get_verified_role()

    msg = await ctx.send(gets(String.VERIFYALL_CONFIRMATION).format(verified_role_name=verified_role.name, emoji=StandardEmoji.OK))
    await msg.add_reaction(UnicodeEmoji.OK)

    try:
        def is_confirmation(reaction: Reaction, member: Member):
            if reaction.message.id != msg.id:
                return False

            if member.id != member.guild.owner.id:
                return False

            if reaction.emoji != UnicodeEmoji.OK:
                return False

            return True

        _reaction, _user = await bot.wait_for("reaction_add", timeout=30, check=is_confirmation)
    except TimeoutError:
        await ctx.send(gets(String.VERIFYALL_TIMEOUT))
    else:
        VERIFYALL_STARTING = gets(String.VERIFYALL_STARTING)
        VERIFYALL_PROGRESS = gets(String.VERIFYALL_PROGRESS)
        VERIFYALL_DONE = gets(String.VERIFYALL_DONE)

        progress = await ctx.send(
            VERIFYALL_STARTING + VERIFYALL_PROGRESS.format(current=0, total=ctx.guild.member_count)
        )

        count = 0
        errored = 0
        async for member in ctx.guild.fetch_members(limit=None):
            try:
                await member.add_roles(verified_role, reason="!verifyall")
            except HTTPException:
                errored += 1
            else:
                count += 1

            if count % 10 == 0:
                await progress.edit(
                    content=VERIFYALL_STARTING + VERIFYALL_PROGRESS.format(current=count, total=ctx.guild.member_count)
                )

        await progress.edit(
            content=VERIFYALL_STARTING + VERIFYALL_DONE.format(
                verified_role_name=verified_role.name, total_done=count, total_errored=errored
            )
        )


@cmd_verifyall.error
async def cmd_verifyall_error(ctx: Context, _: CheckFailure):
    await ctx.send(gets(String.CMD_NOT_ALLOWED_FOR_USER))


#############
# Normal commands
#############
@bot.command(name="verify", brief="Verify yourself if you haven't already")
async def cmd_verify(ctx: Context):
    verified_role = await get_verified_role()

    if verified_role in ctx.author.roles:
        await ctx.send(gets(String.MANUAL_VERIFICATION_NO_NEED).format(user_mention=ctx.author.mention))
    else:
        await ctx.send(gets(String.MANUAL_VERIFICATION).format(user_mention=ctx.author.mention))
        await begin_verification(ctx.author)


@bot.command(name="unverify", brief="Remove the verified role from yourself")
async def cmd_removerole(ctx: Context):
    success_role = await get_verified_role()
    author: Member = ctx.author

    await author.remove_roles(success_role)
    await ctx.message.add_reaction("✅")


@bot.command(name="ping", brief="The bot responds if alive")
async def cmd_ping(ctx: Context):
    await ctx.send("Pong! :ping_pong:")


@bot.command(name="about", brief="A bit about the bot")
async def cmd_about(ctx: Context):
    await ctx.send(gets(String.BOT_ABOUT).format(bot_mention=bot.user.mention, bot_version=__version__))

# Run everything
bot.run(BOT_TOKEN)
