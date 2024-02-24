import disnake, sqlite3
from disnake.ext import commands

class thirdGrade(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
	
	@commands.Cog.listener()
	async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
		if before.channel is None and after.channel is not None:
			if after.channel.id == 1144931882644017223:
				await member.move_to(None)
				conn = sqlite3.connect('account.db');c = conn.cursor()
				c.execute(f"SELECT phone,ok FROM account WHERE discordId={member.id}")
				n = c.fetchone()
				if n and n[0]: await member.add_roles(member.guild.get_role(1101874416448700436))
				if n and n[1]: await member.add_roles(member.guild.get_role(1023898492797714452))

def setup(bot: commands.Bot):
	bot.add_cog(thirdGrade(bot))