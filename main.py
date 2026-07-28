import discord
from discord import app_commands
from api import users, commands
from . import configuration, event

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Logging(bot=bot))

class Logging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="logging", description="Configure which channels which logs are sent to")
    async def channel(self, interaction: discord.Interaction):
        if not await users.has_permission(interaction.guild.id, interaction.user.id, "sonny_logging:log_admin"):
            return await interaction.response.send_message(":warning: No permission.",ephemeral=True)
        await interaction.response.send_message(view=configuration.ConfigButton())
    
    async def get_channel(self, action):
        if action not in configuration.logging_config["logged_actions"]: return False
        if configuration.logging_config["logged_actions"][action] == 0: return False
        channel = self.bot.get_partial_messageable(configuration.logging_config["logged_actions"][action])
        return channel
    
    @commands.Cog.listener()
    async def on_message_edit(self, previous: discord.Message, current: discord.Message):
        if previous.author.bot: return
        if previous.content == current.content: return
        channel = await self.get_channel("message_edit")
        if channel == False: return
        await event.edit_message(previous, current, channel)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot: return
        channel = await self.get_channel("message_delete")
        if channel == False: return
        await event.delete_message(message, channel)

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        if entry.action.name == "message_delete": return
        channel = await self.get_channel(entry.action.name)
        if channel == False: return
        await event.audit_log_entry(entry, channel)

