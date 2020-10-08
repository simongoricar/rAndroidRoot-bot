from discord.ext.commands import Context, check

from .config import SPECIAL_USERS_IDS


def decorate_check(predicate):
    """
    Source: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.check_any
    This properly decorates the normal checks for use in check_any.
    """
    return check(predicate)


async def is_server_owner(ctx: Context):
    return ctx.author.id == ctx.guild.owner.id


async def is_special_user(ctx: Context):
    return ctx.author.id in SPECIAL_USERS_IDS
