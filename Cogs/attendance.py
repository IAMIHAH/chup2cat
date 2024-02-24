import disnake, datetime, calendar
from disnake.ext import commands
from modules.attendance import getAttendance, getAttendanceCalendar

class attendance(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.slash_command(
		name="출석체크",
		description="이달의 출석 달력!",
		options=[
			disnake.Option(
				name="user",
				description="유저명 (관리자전용)",
				type=disnake.OptionType.user
			)
		],
		guild_ids=[812664224512868382,742188157424107679]
	)
	async def attendance_slashCommand(
		self, i: disnake.CommandInteraction,
		user: disnake.Member=None
	):
		if user and not i.user.guild_permissions.administrator: user = i.user
		if not user: user = i.user
		await getAttendance(user)
		now = datetime.datetime.now()
		last_day = calendar.monthrange(now.year, now.month)[1]
		embeds = [
			disnake.Embed(
				title="ℹ️ 출석체크 안내", color=0xabcdef,
				description=f"채팅 경험치 획득을 2회 하게 되면\n자동으로 그 날의 출석체크(🎖️)가 완료돼요!\n\n`7`일 연속 출석 시 `20` 경험치를 지급해요!\n`{last_day}`일 연속 출석 시 `50` 경험치를 추가로 지급해요!"
			)
		]
		embeds.append( disnake.Embed(title=f"✅ {now.year}년 {now.month}월", color=0x00ff00, description=f"{await getAttendanceCalendar(i.user)}") )
		await i.response.send_message(embeds=embeds, ephemeral=True)

def setup(bot: commands.Bot):
	bot.add_cog(attendance(bot))