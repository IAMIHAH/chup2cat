import disnake
from disnake.ext import commands
from modules.gamble.blackjack import blackjack_start
from modules.gamble.oddEven import oddeven_start

class gamble(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.slash_command(
		name="도박",
		guild_ids=[812664224512868382,742188157424107679]
	)
	async def gamble_slashCommand(self, i: disnake.CommandInteraction):
		pass

	@gamble_slashCommand.sub_command(
		name="홀짝",
		description="홀수일까요, 짝수일까요?"
	)
	async def oddEven_slashCommands(
		self, i: disnake.CommandInteraction,
		betting: int = commands.Param(
			name="베팅",
			description="베팅할 냥코인 수 입력"
		),
		guess: int = commands.Param(
			name="정답",
			description="홀 또는 짝.",
			choices=[ disnake.OptionChoice(name="홀수", value=1),
					  disnake.OptionChoice(name="짝수", value=0) ]
		)
	):
		await oddeven_start(i, betting, guess)
	
	@gamble_slashCommand.sub_command(
		name="블랙잭",
		description="카드의 합이 21에 가깝도록!",
	)
	async def blackjack_sc(
		self, i: disnake.CommandInteraction,
		betting: int = commands.Param(
			name="베팅",
			description="베팅할 냥코인 수 입력"
		),
	):
		await blackjack_start(i, betting)

def setup(bot: commands.Bot):
	bot.add_cog(gamble(bot))