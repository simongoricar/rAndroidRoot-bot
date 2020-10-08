from discord.ext.commands import Context


async def is_server_owner(ctx: Context):
    return ctx.author.id == ctx.guild.owner.id
