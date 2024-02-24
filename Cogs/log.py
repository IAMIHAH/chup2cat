import datetime
import disnake, sqlite3
from disnake.ext import commands
from modules.embed import makeErrorEmbed
from modules.log import fetchLogs, fetchLogsWithEvent, fetchLog
from modules.item import getItemEmoji, getItemName

class LogsSelect(disnake.ui.Select):
	def __init__(
		self,
		user: disnake.Member,
		logsItems: list[disnake.SelectOption]
	):
		self.user = user
		self.logsItems = logsItems
		super().__init__(custom_id=f"log-{user.id}", placeholder=f"{user.name[:8] + '...' if len(user.name) > 7 else user.name}님의 기록", options=logsItems)
	
	async def callback(self, i: disnake.Interaction):
		userId = int(self.custom_id.split("-")[1])
		event = self.values[0].split("/")[0]
		time = self.values[0].split("/")[1]
		# 0: time / 1: event / 2: userId / 3: gainedExp
		# 4: cmdUserId / 5: item / 6: itemAmount / 7: chId / 8: msgId

		# ExpFromChat / ExpFromAdmin / UseItem / GetItem / AddItem / RemoveItem
		x = await fetchLog(userId=userId, time=time, event=event)
		cmdUser = x[4]
		if cmdUser == 1: cmdUser = "Unknown"
		elif cmdUser == 2: cmdUser = "시스템"
		elif cmdUser == 3: cmdUser = "첩첩냥 운영자" if i.locale == disnake.Locale.ko else "Chupchupcat Administrator"
		elif cmdUser == 4: cmdUser = "시즌 종료 보상" if i.locale == disnake.Locale.ko else "Reward for Season End"
		elif cmdUser and len(cmdUser) < 18: cmdUser = "Unknown"
		description = "*(알 수 없음)*" if i.locale == disnake.Locale.ko else "*(Unknown)*"
		if str(cmdUser).isdigit():
			admin = f"<@{cmdUser}>"
		else:
			admin = f"`{cmdUser}`"
		if x[1] == "ExpFromChat": description = f"[메시지](https://discord.com/channels/812664224512868382/{x[7]}/{x[8]})를 전송하여 채팅 경험치 획득" if i.locale == disnake.Locale.ko else f"Earn EXP by sent [message](https://discord.com/channels/812664224512868382/{x[7]}/{x[8]})"
		if x[1] == "ExpFromAdmin":
			if cmdUser > 0: description = f"관리자 {admin}님이 경험치 지급" if i.locale == disnake.Locale.ko else f"Administrator {admin} gave EXP"
			else: description = f"관리자 {admin}님이 경험치 회수" if i.locale == disnake.Locale.ko else f"Administrator {admin} retrieves EXP"
		if x[1] == "UseItem": description = f"아이템 사용" if i.locale == disnake.Locale.ko else "Use items"
		if x[1] == "GetItem": description = f"아이템 획득" if i.locale == disnake.Locale.ko else "Got items"
		if x[1] == "AddItem" or x[1] == "RemoveItem":
			if x[1] == "AddItem": description = f"관리자 {admin}님이 아이템 지급" if i.locale == disnake.Locale.ko else f"Administrator {admin} gave items"
			if x[1] == "RemoveItem": description = f"관리자 {admin}님이 아이템 회수" if i.locale == disnake.Locale.ko else f"Administrator {admin} retrieves items"
		if x[1] == "SeasonEnd": description = f"시즌 종료" if i.locale == disnake.Locale.ko else f"Season end"
		if x[1] == "Attendance": description = f"출석체크" if i.locale == disnake.Locale.ko else f"Attendance"
		if x[1] == "AttendanceMore7": description = f"출석체크 7일" if i.locale == disnake.Locale.ko else f"Attendance 7 days"
		if x[1] == "AttendanceMore31": description = f"출석체크 1개월" if i.locale == disnake.Locale.ko else f"Attendance a month"
		embed = disnake.Embed(
			title="자세한 로그 정보" if i.locale == disnake.Locale.ko else "Log details",
			description=f"{description}"
		)
		if x[3]: embed.add_field(name="획득한 경험치" if i.locale == disnake.Locale.ko else "Obtained EXP", value=f"`{x[3]}`")
		if x[7]: embed.add_field(name="채널" if i.locale == disnake.Locale.ko else "Channel", value=f"<#{x[7]}>")
		if x[8]: embed.add_field(name="메시지 아이디" if i.locale == disnake.Locale.ko else "Message ID", value=f"[{x[8]}](https://discord.com/channels/812664224512868382/{x[7]}/{x[8]})")
		if x[5]:
			emoji = await getItemEmoji(x[5])
			embed.add_field(name="아이템" if i.locale == disnake.Locale.ko else "Item", value=f"{emoji if emoji else '🔘'} {await getItemName(x[5], locale=i.locale)}")
		if x[6]: embed.add_field(name="아이템 수량" if i.locale == disnake.Locale.ko else "Item Amount", value=f"`{x[6]}`")
		embed.add_field(name="시각" if i.locale == disnake.Locale.ko else "Time", value=f"KST {datetime.datetime.fromtimestamp(x[0]).strftime('%Y-%m-%d %H:%M:%S')}", inline=False)
		for x in range(len(self.logsItems)):
			self.logsItems[x].default = False
			if self.logsItems[x].value == self.values[0]:
				self.logsItems[x].default = True
		await i.response.edit_message(content="", embed=embed, view=LogsView(user=self.user, logsItems=self.logsItems))

class LogsView(disnake.ui.View):
	def __init__(
		self,
		user: disnake.Member,
		logsItems: list[disnake.SelectOption]
	):
		super().__init__(timeout=180)
		self.add_item(LogsSelect(user=user, logsItems=logsItems))

class Logs(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
	
	@commands.slash_command(
		name=disnake.Localized(
			"log",
			data={
				disnake.Locale.ko: "기록"
			}
		),
		description=disnake.Localized(
			"Check the logs accumulated so far.",
			data={
				disnake.Locale.ko: "지금까지 쌓여온 기록을 확인해요."
			}
		),
		options=[
			disnake.Option(
				name=disnake.Localized(
					"event",
					data={
						disnake.Locale.ko: "구분"
					}
				),
				description=disnake.Localized(
					"Events.",
					data={
						disnake.Locale.ko: "구분."
					}
				),
				choices=[
					disnake.OptionChoice(
						name=disnake.Localized(
							"Experience point from message",
							data={
								disnake.Locale.ko: "채팅에서 얻은 경험치"
							}
						),
						value="ExpFromChat"
					),
					disnake.OptionChoice(
						name=disnake.Localized(
							"Experience point from administrator",
							data={
								disnake.Locale.ko: "관리자에게서 얻은 경험치"
							}
						),
						value="ExpFromAdmin"
					),
					disnake.OptionChoice(
						name=disnake.Localized(
							"Used item",
							data={
								disnake.Locale.ko: "사용한 아이템"
							}
						),
						value="UseItem"
					),
					disnake.OptionChoice(
						name=disnake.Localized(
							"Earned item",
							data={
								disnake.Locale.ko: "얻은 아이템"
							}
						),
						value="GetItem"
					),
					disnake.OptionChoice(
						name=disnake.Localized(
							"Earned item from administrator",
							data={
								disnake.Locale.ko: "관리자에게서 얻은 아이템"
							}
						),
						value="AddItem"
					),
					disnake.OptionChoice(
						name=disnake.Localized(
							"Removed item from administrator",
							data={
								disnake.Locale.ko: "관리자에게 뺏긴 아이템"
							}
						),
						value="RemoveItem"
					)
				]
			),
			disnake.Option(
				name=disnake.Localized(
					"user",
					data={
						disnake.Locale.ko: "유저"
					}
				),
				description=disnake.Localized(
					"User name.",
					data={
						disnake.Locale.ko: "유저명."
					}
				),
				type=disnake.OptionType.user
			)
		]
	)
	async def checkLogsSlashCommands(
		self,
		i: disnake.CommandInteraction,
		event: str = None,
		user: disnake.Member = None
	):
		if user:
			if not i.user.guild_permissions.administrator:
				await i.response.send_message(makeErrorEmbed("권한이 없어요."), ephemeral=True)
				return
		else:
			user = i.user
		if event:
			logs = await fetchLogsWithEvent(userId=user.id, event=event)
		else:
			logs = await fetchLogs(userId=user.id)
		options = []
		for x in logs:
			# 0: time / 1: event / 2: gainedExp
			description = self.shortDesc(x[1], x[2], i.locale)
			options.append(
				disnake.SelectOption(
					label=f"{description}",
					description=f"{datetime.datetime.fromtimestamp(x[0]).strftime('%Y-%m-%d %H:%M:%S')}",
					value=f"{x[1]}/{x[0]}"
				)
			)
		eventDesc = "모든 기록"
		if event:
			eventDesc = f"`{self.shortDesc(event, locale=i.locale)}` 기록만"
		if len(options) > 0:
			embed = disnake.Embed(
				title="📜 첩첩냥 기록 확인하기",
				description=f"지금까지 활동한 {user.mention}님의 {eventDesc}을 모았어요.\n\n한 페이지당 최대 25개까지 조회가 가능해요.\n참고해주세요!",
				color=0xabcdef
			)
			await i.response.send_message(embed=embed, view=LogsView(user=user, logsItems=options), ephemeral=True)
		else:
			desc = ""
			if user == i.user:
				desc = "\n\n지금 당장 채팅을 입력해\n경험치를 얻어보는건 어떤가요? :smile:"
			await i.response.send_message(embed=makeErrorEmbed(f"조회된 첩첩냥 기록이 없어요!{desc}"), ephemeral=True)

	def shortDesc(self, key: str, exp: float=None, locale: disnake.Locale=disnake.Locale.ko) -> str:
		description = "(알 수 없음)"
		if key == "ExpFromChat": description = "채팅 경험치 획득" if locale == disnake.Locale.ko else "Earn EXP by sent message"
		if key == "ExpFromAdmin":
			if exp:
				if exp > 0: description = "관리자가 경험치 지급" if locale == disnake.Locale.ko else "Administrator gave EXP"
				else: description = "관리자가 경험치 회수" if locale == disnake.Locale.ko else "Administrator retrieves EXP"
			else:
				description = "관리자가 경험치 관리" if locale == disnake.Locale.ko else "Administrator managed your EXP"
		if key == "UseItem": description = "아이템 사용" if locale == disnake.Locale.ko else "Used items"
		if key == "GetItem": description = "아이템 획득" if locale == disnake.Locale.ko else "Got items"
		if key == "AddItem": description = "관리자가 아이템 지급" if locale == disnake.Locale.ko else "Administrator gave items"
		if key == "RemoveItem": description = "관리자가 아이템 회수" if locale == disnake.Locale.ko else "Administrator retrieves items"
		if key == "SeasonEnd": description = "시즌 종료" if locale == disnake.Locale.ko else "Season end"
		return description

def setup(bot: commands.Bot):
	bot.add_cog(Logs(bot))