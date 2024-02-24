import disnake
from disnake.ext import commands

class Role(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
	
	@commands.Cog.listener()
	async def on_raw_reaction_add(self, reaction: disnake.RawReactionActionEvent):
		if reaction.channel_id == 891620884622761994:
			ch = await self.bot.fetch_channel(reaction.channel_id)
			msg = await ch.fetch_message(reaction.message_id)
			user = await ch.guild.fetch_member(reaction.user_id)
			await user.add_roles(msg.role_mentions[0])
	
	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, reaction: disnake.RawReactionActionEvent):
		if reaction.channel_id == 891620884622761994:
			ch = await self.bot.fetch_channel(reaction.channel_id)
			msg = await ch.fetch_message(reaction.message_id)
			user = await ch.guild.fetch_member(reaction.user_id)
			await user.remove_roles(msg.role_mentions[0])

def setup(bot: commands.Bot):
	bot.add_cog(Role(bot))