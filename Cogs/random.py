import random
import disnake, sqlite3
from disnake.ext import commands

class CRandom(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
	
	@commands.slash_command(
		name="랜덤",
		description="랜덤뽑기",
		options=[
			disnake.Option(
				name="텍스트",
				description="랜덤을 돌릴 텍스트를 쉼표로 나누어주세요.",
				type=disnake.OptionType.string,
				required=True
			),
			disnake.Option(
				name="횟수",
				description="랜덤을 돌릴 횟수를 입력해주세요.",
				type=disnake.OptionType.integer,
				required=False
			)
		],
		connectors={
			"텍스트": "texts",
			"횟수": "times"
		}
	)
	async def random(
		self, i: disnake.CommandInteraction,
		texts: str, times: int = 1
	):
		texts: list = texts.split(',')
		results = []
		for x in range(times):
			_i = texts[random.randint(0, len(texts)-1)]
			results.append(_i)
			texts.remove(_i)
		await i.response.send_message(' / '.join(results).replace("_", "\_"))

def setup(bot: commands.Bot):
	bot.add_cog(CRandom(bot))