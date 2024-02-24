import disnake, sqlite3, mcuuid, re
from disnake.ext import commands
from modules.embed import makeErrorEmbed

class coren(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.slash_command(
		name="코른",
		guild_ids=[812664224512868382,742188157424107679]
	)
	async def coren_slashCommand(self, i: disnake.CommandInteraction):
		pass

	@coren_slashCommand.sub_command(
		name="사전예약",
		description="COREN: Season LUNATIC 사전예약을 하고 보상을 챙겨가세요!"
	)
	async def corenEarlyReservation(
		self, i: disnake.CommandInteraction,
		nick: str = commands.Param(
			name="닉네임",
			description="선점할 닉네임"
		)
	):
		conn = sqlite3.connect('auth.db', isolation_level=None)
		c = conn.cursor()
		c.execute(f"select minecraft from user where id={i.user.id}")
		n = c.fetchone()
		if n:
			minecraft = n[0]
		else:
			await i.response.send_message(embed=makeErrorEmbed("마인크래프트 계정이 연동되어있지 않아요.\n[여기](https://c.ihah.me/login/minecraft)를 통해 마인크래프트 계정을 연동해주세요!"), ephemeral=True)
			return
		if len(nick) < 2 or len(nick) > 6:
			await i.response.send_message(embed=makeErrorEmbed("닉네임은 2글자 이상 6글자 이하로 입력해주세요."), ephemeral=True)
			return
		if ' ' in nick:
			await i.response.send_message(embed=makeErrorEmbed("닉네임에 공백을 포함할 수 없어요."), ephemeral=True)
			return
		conn = sqlite3.connect("coren.db")
		c = conn.cursor()
		c.execute(f"SELECT userId,nickname FROM earlyReservation WHERE userId={i.user.id}")
		n = c.fetchone()
		c.execute(f"SELECT userId FROM earlyReservation WHERE nickname='{nick}'")
		u = c.fetchone()
		if u == None:
			if n:
				c.execute(f"UPDATE earlyReservation SET nickname='{nick}' WHERE userId={i.user.id}")
				conn.commit()
				embed = disnake.Embed(
					title="✅ 사전예약 닉네임 변경 완료!",
					description="헬리네 왕국 통행증을 수정했어요. 나중에 봐요!",
					color=0x00ff00
				)
				embed.add_field(name="마인크래프트 닉네임", value=f"`{mcuuid.MCUUID(uuid=minecraft).name}`")
				embed.add_field(name="코른 사전예약 닉네임", value=f"`{n[1]}` → `{nick}`")
				await i.response.send_message(embed=embed)
			else:
				c.execute(f"INSERT INTO earlyReservation VALUES ({i.user.id}, '{nick}')")
				conn.commit()
				embed = disnake.Embed(
					title="✅ 코른 사전예약 완료!",
					description="헬리네 왕국 통행증을 발급했어요. 나중에 봐요!",
					color=0x00ff00
				)
				embed.add_field(name="마인크래프트 닉네임", value=f"`{mcuuid.MCUUID(uuid=minecraft).name}`")
				embed.add_field(name="코른 사전예약 닉네임", value=f"`{nick}`")
				await i.response.send_message(embed=embed)
		else:
			await i.response.send_message(embed=makeErrorEmbed("이미 다른 유저가 사용중인 닉네임이에요."), ephemeral=True)
		conn.close()

def setup(bot: commands.Bot):
	bot.add_cog(coren(bot))