import asyncio
import disnake, sqlite3, random, time
from disnake.ext import commands
from config import SEASON, SEASON_TEXT, SERVER, churList
from modules.attendance import attendanceUp, getAttendance, getAttendanceMore
# from modules.chur import churAdd
from modules.embed import makeErrorEmbed
from modules.event_point import eventPointAdd, getEventPoint
from modules.items.expbottle import getExpBottle
from modules.log import addLog
from modules.exp import *
from modules.message import numberJosa

class Leveling(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_message(
		self,
		msg: disnake.Message
	):
		if msg.author.bot:
			return
		msgChannel = [
			812664224512868387, 1020657071290581043, 816292528645996584, 
			884068385284063272, 814450977243136020, 1020655644946215012,

			1046067291621691442, 891241928056774717, 1020892409774751784,
			1002434863393157230, 955107377118593084, 940207026158587905,
			813758509732200533, 1060947795349090424,

			970331436357922896, 853498964350861322,

			1096746311421804564
		]
		msgSet = False
		if msg.channel.id in msgChannel:
			msgSet = True
		if msg.channel.type == disnake.ChannelType.public_thread or msg.channel.type == disnake.ChannelType.private_thread:
			if msg.channel.parent.id in msgChannel:
				msgSet = True
		if msgSet:
			if SERVER != "PRODUCTION" and msg.channel.id != 1096746311421804564: return
			lv, xp = await expNow(user=msg.author)
			cooldown = await expCooldown(user=msg.author)
			if cooldown <= time.time():
				if "호박" in msg.content or "트릭" in msg.content:
					return
				exp = random.uniform(15, 25)
				try:
					if msg.author.roles.index(msg.guild.premium_subscriber_role):
						exp += exp*0.02
				except ValueError:
					exp += 0
				exp = round(exp, 3)
				if lv <= 15: exp += exp*0.03
				exp += exp*(await getExpBottle(user=msg.author))
				await expAdd(user=msg.author, exp=exp, cooldown=time.time()+40)
				await addLog(event="ExpFromChat", userId=msg.author.id, gainedExp=exp, chId=msg.channel.id, msgId=msg.id)
				await attendanceUp(user=msg.author)
				attend = await getAttendance(user=msg.author)
				levelUp = await expLevelUp(user=msg.author)
				if levelUp:
					await msg.reply(f"**첩첩냥 채팅패스** `{SEASON_TEXT}`\n> 레벨 {levelUp}{numberJosa(levelUp)} 달성했습니다! 🎉")
				if attend == 2:
					await expAdd(user=msg.author, exp=20)
					await addLog(event="Attendance", userId=msg.author.id, gainedExp=20)
					await msg.add_reaction("🎖️")
				if churList[random.randint(0,99)] == "Y": # 이벤트 「첩첩냥은 츄르가 고파요!」
					await eventPointAdd(user=msg.author.id, addPoints=2)
					await msg.add_reaction("🎃")
					await asyncio.sleep(10)
					await msg.remove_reaction("🎃", self.bot.user)

	@commands.slash_command(
		name=disnake.Localized(
			"info",
			data={
				disnake.Locale.ko: "정보"
			}
		),
		description=disnake.Localized(
			"Check your account information",
			data={
				disnake.Locale.ko: "첩첩냥 계정 정보를 확인해요."
			}
		),
		options=[
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
						disnake.Locale.ko: "유저 이름."
					}
				),
				type=disnake.OptionType.user
			),
			disnake.Option(
				name=disnake.Localized(
					"season",
					data={
						disnake.Locale.ko: "시즌"
					}
				),
				description=disnake.Localized(
					"Season.",
					data={
						disnake.Locale.ko: "시즌."
					}
				),
				type=disnake.OptionType.string,
				autocomplete=True
			),
		],
		guild_ids=[812664224512868382]
	)
	async def myLevel(
		self,
		i: disnake.CommandInteraction,
		user: disnake.Member = None,
		season: str = SEASON
	):
		if user:
			if not i.user.guild_permissions.administrator:
				await i.response.send_message(":warning: 권한이 없어요.", ephemeral=True)
				return
		if not user:
			user = i.user
		now = await expNow(user=user, season=season)
		if season == SEASON: season = SEASON_TEXT
		embed = disnake.Embed(
			title="첩첩냥 채팅패스 정보",
			description=f"SEASON `{season}`\n{user.mention}님의 정보"
		)
		embed.add_field(name="레벨", value=f"{now[1]}")
		embed.add_field(name="경험치", value=f"{now[0]} / {expNextLevelExp(now[1]+1)}")
		await i.response.send_message(embed=embed, ephemeral=True)

	@myLevel.autocomplete("season")
	async def seasonList(self, i: disnake.CommandInteraction, search: str):
		conn = sqlite3.connect("user.db", isolation_level=None)
		c = conn.cursor()
		c.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table', 'view') ORDER BY 1;")
		n = c.fetchall()
		data=[]
		for x in n:
			data.append(x[0])
		return data

	@commands.slash_command(
		name=disnake.Localized(
			"exp",
			data={
				disnake.Locale.ko: "경험치"
			}
		),
		guild_ids=[812664224512868382]
	)
	async def expSlashCommand(self, i: disnake.CommandInteraction):
		pass

	@expSlashCommand.sub_command(
		name=disnake.Localized(
			"add",
			data={
				disnake.Locale.ko: "추가"
			}
		),
		description=disnake.Localized(
			"Add an user's experience point.",
			data={
				disnake.Locale.ko: "유저의 경험치를 추가합니다."
			}
		),
		options=[
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
						disnake.Locale.ko: "유저 이름."
					}
				),
				type=disnake.OptionType.user,
				required=True
			),
			disnake.Option(
				name=disnake.Localized(
					"exp",
					data={
						disnake.Locale.ko: "경험치"
					}
				),
				description=disnake.Localized(
					"amount of experience point.",
					data={
						disnake.Locale.ko: "경험치의 양."
					}
				),
				type=disnake.OptionType.number,
				required=True
			)
		]
	)
	async def addExpSlashCommands(
		self,
		i: disnake.CommandInteraction,
		user: disnake.Member,
		exp: float
	):
		if not i.user.guild_permissions.administrator:
			await i.response.send_message(makeErrorEmbed("권한이 없어요."), ephemeral=True)
			return
		expBefore = await expNow(user=user)
		await expAdd(user=user, exp=exp)
		await addLog(event="ExpFromAdmin", userId=user.id, gainedExp=exp, cmdUserId=i.user.id)
		levelUp = await expLevelUp(user=user)
		if levelUp:
			ch : disnake.TextChannel = await self.bot.fetch_channel(812664224512868387)
			await ch.send(f"{user.mention}\n**첩첩냥 채팅패스** `{SEASON_TEXT}`\n> 레벨 {levelUp}{numberJosa(levelUp)} 달성했습니다! 🎉")
		_expNow = await expNow(user=user)
		embed = disnake.Embed(
			title="✅ 경험치 지급 완료!",
			description=f"{user.mention}님에게 경험치를 지급했습니다.",
			color=0x00ff00
		)
		embed.add_field(
			name="레벨",
			value=f"{expBefore[1]} → {_expNow[1]}"
		)
		embed.add_field(
			name="경험치",
			value=f"{expBefore[0]} → {_expNow[0]}"
		)
		await i.response.send_message(embed=embed)

	@expSlashCommand.sub_command(
		name=disnake.Localized(
			"remove",
			data={
				disnake.Locale.ko: "제거"
			}
		),
		description=disnake.Localized(
			"Subtract an user's experience point.",
			data={
				disnake.Locale.ko: "유저의 경험치를 제거합니다."
			}
		),
		options=[
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
						disnake.Locale.ko: "유저 이름."
					}
				),
				type=disnake.OptionType.user,
				required=True
			),
			disnake.Option(
				name=disnake.Localized(
					"exp",
					data={
						disnake.Locale.ko: "경험치"
					}
				),
				description=disnake.Localized(
					"amount of experience point.",
					data={
						disnake.Locale.ko: "경험치의 양."
					}
				),
				type=disnake.OptionType.number,
				required=True
			)
		]
	)
	async def removeExpSlashCommands(
		self,
		i: disnake.CommandInteraction,
		user: disnake.Member,
		exp: float
	):
		if not i.user.guild_permissions.administrator:
			await i.response.send_message(makeErrorEmbed("권한이 없어요."), ephemeral=True)
			return
		expBefore = await expNow(user=user)
		await expAdd(user=user, exp=-exp)
		await addLog(event="ExpFromAdmin", userId=user.id, gainedExp=exp, cmdUserId=i.user.id)
		await expLevelDown(user=user)
		_expNow = await expNow(user=user)
		embed = disnake.Embed(
			title="✅ 경험치 제거 완료!",
			description=f"{user.mention}님에게서 경험치를 제거했습니다.",
			color=0x00ff00
		)
		embed.add_field(
			name="레벨",
			value=f"{expBefore[1]} → {_expNow[1]}"
		)
		embed.add_field(
			name="경험치",
			value=f"{expBefore[0]} → {_expNow[0]}"
		)
		await i.response.send_message(embed=embed)
	
	@commands.slash_command(
		name=disnake.Localized(
			"calculate",
			data={
				disnake.Locale.ko: "계산"
			}
		),
		description=disnake.Localized(
			"Calculate leveling.",
			data={
				disnake.Locale.ko: "레벨링에 관한 내용을 계산합니다."
			}
		),
		options=[
			disnake.Option(
				name=disnake.Localized(
					"mode",
					data={
						disnake.Locale.ko: "모드"
					}
				),
				description=disnake.Localized(
					"Mode. (Write contents in brackets to 'value')",
					data={
						disnake.Locale.ko: "모드. (대괄호 안에 있는 내용을 '값'에 쓰세요.)"
					}
				),
				required=True,
				choices=[
					# disnake.OptionChoice(
					# 	name=disnake.Localized(
					# 		"specific exp to level",
					# 		data={
					# 			disnake.Locale.ko: "[특정 경험치]를 레벨로 환산"
					# 		}
					# 	),
					# 	value="exp-to-level"
					# ),
					disnake.OptionChoice(
						name=disnake.Localized(
							"exp for reaching a [specific level]",
							data={
								disnake.Locale.ko: "[특정 레벨]을 달성하기 위한 경험치"
							}
						),
						value="level-to-exp"
					),
					disnake.OptionChoice(
						name=disnake.Localized(
							"now to [specific level]",
							data={
								disnake.Locale.ko: "지금부터 [특정 레벨]까지"
							}
						),
						value="now-to-level"
					)
				]
			),
			disnake.Option(
				name=disnake.Localized(
					"value",
					data={
						disnake.Locale.ko: "값"
					}
				),
				description=disnake.Localized(
					"value",
					data={
						disnake.Locale.ko: "값"
					}
				),
				required=True,
				type=disnake.OptionType.number
			)
		],
		guild_ids=[812664224512868382]
	)
	async def calculateSlashCommands(
		self,
		i: disnake.CommandInteraction,
		mode: str,
		value: float
	):
		if mode == "level-to-exp":
			if value.is_integer():
				result = expNextLevelExp(int(value))
				mode = f"{int(value)} 레벨을 달성하기 위한 경험치"
			else:
				await i.response.send_message(makeErrorEmbed("값이 잘못되었어요."), ephemeral=True)
				return
		elif mode == "now-to-level":
			if value.is_integer():
				mode = f"현재 레벨에서 {int(value)} 레벨까지 필요한 경험치"
				expGo = expNextLevelExp(int(value))
				expNow = await expNow(user=i.author)
				result = expGo - expNow[0]
			else:
				await i.response.send_message(makeErrorEmbed("값이 잘못되었어요."), ephemeral=True)
				return
		else:
			await i.response.send_message(makeErrorEmbed("모드가 잘못되었어요."), ephemeral=True)
			return
		
		embed = disnake.Embed(
			title="✅ 계산 완료!",
			description=f"계산을 완료했어요.",
			color=0x00ff00
		)
		embed.add_field(
			name=mode,
			value=f"`{round(result, 3)}`"
		)
		await i.response.send_message(embed=embed)

def setup(bot: commands.Bot):
	bot.add_cog(Leveling(bot))