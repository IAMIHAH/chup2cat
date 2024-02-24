import disnake, sqlite3
from disnake.ext import commands

from modules.embed import makeErrorEmbed
from modules.event_point import eventPointAdd, getEventPoint

class eventcog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
	
	@commands.slash_command(
		name="execute",
		description="execute event commands",
		guild_ids=[742188157424107679]
	)
	async def msgissky_slashCommand(self, i: disnake.CommandInteraction):
		if i.user.id != self.bot.owner_id: await i.response.send_message(embed=makeErrorEmbed("You are not owner!"), ephemeral=True)
		ch = self.bot.get_channel(812664224512868387)
		embed = disnake.Embed(
			title="《말이 곧 하늘이다》 선착순 포인트 획득!",
			description="채팅을 입력하면 **선착순 5명**에게 5포인트부터 차등으로 포인트를 지급*!*"
		)
		await ch.send(embed=embed)
		listPeople = []
		def check(m: disnake.Message):
			if m.author.id in listPeople: return False
			listPeople.append(m.author.id)
			return True
		pointEmoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
		for x in range(5):
			try:
				msg: disnake.Message = await self.bot.wait_for('message', check=check)
				await eventPointAdd(user=msg.author.id, addPoints=5-(len(listPeople)-1), point="point")
				await msg.add_reaction(pointEmoji[5-len(listPeople)])
			except:
				await ch.send(embed=makeErrorEmbed("`p:event_msg-is-sky`\n일시적인 내부 오류가 발생했어요."))
				return

	@commands.slash_command(
		name="이벤트",
		description="이벤트 관련",
		guild_ids=[812664224512868382,742188157424107679]
	)
	async def event_slashcmd(self, i: disnake.CommandInteraction):
		pass

	@event_slashcmd.sub_command(
		name="포인트",
		description="이벤트 포인트를 조회해요."
	)
	async def event_point(self, i: disnake.CommandInteraction):
		embed = disnake.Embed(
			title="이벤트 포인트",
			description=f"현재 보유중인 이벤트 포인트는 `{'{:,}'.format(await getEventPoint(i.user.id))}`점입니다."
		)
		await i.response.send_message(embed=embed,ephemeral=True)

def setup(bot: commands.Bot):
	bot.add_cog(eventcog(bot))