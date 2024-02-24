import disnake, sqlite3
from disnake.ext import commands

class gacha(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
	
	@commands.slash_command(
		name="제작소",
		description="제작소에서 다양한 첩첩냥 아이템을 제작해보세요!",
		guild_ids=[812664224512868382,742188157424107679]
	)
	async def gacha_slashCommand(self, i: disnake.CommandInteraction):
		pass

def setup(bot: commands.Bot):
	bot.add_cog(gacha(bot))