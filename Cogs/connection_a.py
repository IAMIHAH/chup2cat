import disnake, sqlite3, asyncio
from disnake.ext import commands
from mcuuid import MCUUID
from config import helix

class Management(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
	
	@commands.Cog.listener()
	async def on_member_join(self, member: disnake.Member):
		await asyncio.sleep(1)
		conn = sqlite3.connect('account.db', isolation_level=None)
		c = conn.cursor()
		c.execute(f"select twitchId,ok from account where discordId={member.id}")
		n = c.fetchone()
		print(n)
		twitch = helix.user(n[0])
		await member.edit(nick=f"{twitch.display_name}")
		if n[1] == 1:
			await member.add_roles(member.guild.get_role(812668523464753192))
			await member.add_roles(member.guild.get_role(1023898492797714452))
			await member.remove_roles(member.guild.get_role(889825272927498251))
		else:
			await member.add_roles(member.guild.get_role(889825272927498251))
	
	@commands.slash_command(
		name=disnake.Localized(
			"user",
			data={
				disnake.Locale.ko: "유저"
			}
		),
		guild_ids=[812664224512868382]
	)
	async def user_slash(self, i: disnake.CommandInteraction):
		pass

	@user_slash.sub_command(
		name=disnake.Localized(
			"discord",
			data={
				disnake.Locale.ko: "디스코드"
			}
		),
		description=disnake.Localized(
			"Search Twitch user from Discord account.",
			data={
				disnake.Locale.ko: "디스코드 유저를 검색하여 트위치 유저를 찾습니다."
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
					"Discord user.",
					data={
						disnake.Locale.ko: "디스코드 유저."
					}
				),
				type=disnake.OptionType.user,
				required=True
			)
		]
	)
	async def user_slash_discord(
		self,
		i: disnake.CommandInteraction,
		user: disnake.Member
	):
		conn = sqlite3.connect('auth.db', isolation_level=None)
		c = conn.cursor()
		c.execute(f"select twitch from user where id={user.id}")
		n = c.fetchone()
		if n == None or n[0] == None:
			await i.response.send_message(f"{user.mention}님의 연동 정보를 찾을 수 없어요.", ephemeral=True)
		else:
			twitch = helix.user(n[0])
			display_name = twitch.display_name.replace('_', '\_')
			login = twitch.login.replace('_', '\_')
			await i.response.send_message(f"{user.mention}님은 {display_name}{'('+login+')' if twitch.display_name != twitch.login else ''}입니다.", ephemeral=True)

	@user_slash.sub_command(
		name=disnake.Localized(
			"twitch",
			data={
				disnake.Locale.ko: "트위치"
			}
		),
		description=disnake.Localized(
			"Search Discord user from Twitch account.",
			data={
				disnake.Locale.ko: "트위치 유저를 검색하여 디스코드 유저를 찾습니다."
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
					"Twitch user ID.",
					data={
						disnake.Locale.ko: "트위치 유저 ID."
					}
				),
				type=disnake.OptionType.string,
				required=True
			)
		]
	)
	async def user_slash_twitch(
		self,
		i: disnake.CommandInteraction,
		user: str
	):
		conn = sqlite3.connect('auth.db', isolation_level=None)
		c = conn.cursor()
		twitch = helix.user(user)
		if twitch == None:
			await i.response.send_message("올바르지 않은 트위치 유저에요.", ephemeral=True)
			return
		c.execute(f"select id from user where twitch={twitch.id}")
		n = c.fetchone()
		display_name = twitch.display_name.replace('_', '\_')
		login = twitch.login.replace('_', '\_')
		if n == None or n[0] == None:
			await i.response.send_message(f"{display_name}{'('+login+')' if twitch.display_name != twitch.login else ''}님의 연동정보가 없어요.", ephemeral=True)
		else:
			await i.response.send_message(f"{display_name}{'('+login+')' if twitch.display_name != twitch.login else ''}님은 <@{n[0]}> 입니다.", ephemeral=True)

	@user_slash.sub_command(
		name=disnake.Localized(
			"minecraft",
			data={
				disnake.Locale.ko: "마인크래프트"
			}
		),
		description=disnake.Localized(
			"Search Discord and Twitch user from Minecraft account.",
			data={
				disnake.Locale.ko: "마크 유저를 검색하여 디스코드와 트위치 유저를 찾습니다."
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
					"Minecraft nickname.",
					data={
						disnake.Locale.ko: "마인크래프트 닉네임."
					}
				),
				type=disnake.OptionType.string,
				required=True
			)
		]
	)
	async def user_slash_discord(
		self,
		i: disnake.CommandInteraction,
		user: str
	):
		conn = sqlite3.connect('auth.db', isolation_level=None)
		c = conn.cursor()
		u = MCUUID(user)
		c.execute(f"select id,twitch from user where minecraft='{u.uuid}'")
		n = c.fetchone()
		if n == None or n[0] == None:
			await i.response.send_message(f"{user}님의 연동 정보를 찾을 수 없어요.", ephemeral=True)
		else:
			twitch = helix.user(n[1])
			display_name = twitch.display_name.replace('_', '\_')
			login = twitch.login.replace('_', '\_')
			await i.response.send_message(f"{user}(`{u.uuid}`)님은 <@{n[0]}> / {display_name}{'('+login+')' if twitch.display_name != twitch.login else ''}입니다.", ephemeral=True)

	@user_slash.sub_command(
		name=disnake.Localized(
			"connect",
			data={
				disnake.Locale.ko: "강제연동"
			}
		),
		description=disnake.Localized(
			"Connect user Discord and Twitch.",
			data={
				disnake.Locale.ko: "디스코드 유저를 트위치 계정에 강제로 연동시킵니다."
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
					"Discord user.",
					data={
						disnake.Locale.ko: "디스코드 유저."
					}
				),
				type=disnake.OptionType.user,
				required=True
			),
			disnake.Option(
				name=disnake.Localized(
					"twitch",
					data={
						disnake.Locale.ko: "트위치"
					}
				),
				description=disnake.Localized(
					"Twitch user login ID.",
					data={
						disnake.Locale.ko: "트위치 유저 로그인 아이디"
					}
				),
				type=disnake.OptionType.string,
				required=True
			)
		]
	)
	async def user_slash_discord(
		self,
		i: disnake.CommandInteraction,
		user: disnake.Member,
		twitch: str
	):
		conn = sqlite3.connect('auth.db', isolation_level=None)
		c = conn.cursor()
		c.execute(f"select twitch from user where id={user.id}")
		n = c.fetchone()
		if n == None or n[0] == None:
			u = helix.user(twitch)
			if u == None:
				await i.response.send_message(f"트위치 유저를 찾을 수 없습니다.")
				return
			c.execute(f"insert into user(id,twitch) values({user.id}, {u.id})")
			display_name = u.display_name.replace('_', '\_')
			loginID = '('+u.login.replace('_', '\_')+')' if u.display_name != u.login else ''
			await i.response.send_message(f"{user.mention}님의 연동 정보를 `{display_name}{loginID}`로 설정했습니다.", ephemeral=True)
			#c.execute(f"update user set twitch={u.id} where id={user.id}")
		else:
			u = helix.user(n[0])
			_display_name = u.display_name.replace('_', '\_')
			_loginID = '('+u.login.replace('_', '\_')+')' if u.display_name != u.login else ''
			u = helix.user(twitch)
			if u == None:
				await i.response.send_message(f"트위치 유저를 찾을 수 없습니다.")
				return
			display_name = u.display_name.replace('_', '\_')
			loginID = '('+u.login.replace('_', '\_')+')' if u.display_name != u.login else ''
			await i.response.send_message(f"{user.mention}님의 연동 정보를 `{_display_name}{_loginID}`에서 `{display_name}{loginID}`로 변경했습니다.", ephemeral=True)

	@commands.user_command(
		name=disnake.Localized(
			"Connections",
			data={
				disnake.Locale.ko: "연동확인"
			}
		),
		guild_ids=[812664224512868382,742188157424107679]
	)
	async def twitch_discord(self, i: disnake.ApplicationCommandInteraction, user: disnake.Member = None):
		conn = sqlite3.connect('auth.db', isolation_level=None)
		c = conn.cursor()
		c.execute(f"select twitch,minecraft,epicstore from user where id={user.id}")
		n = c.fetchone()
		if n:
			tuser = helix.user(int(n[0]))
			embed = disnake.Embed(
				title="연동 정보 확인",
				description=f"{user.mention}님의 연동 정보입니다."
			)
			if n[0]:
				display_name = tuser.display_name.replace('_', '\_')
				login = tuser.login.replace('_', '\_')
				twitchName = f"{display_name}({login})" if tuser.display_name != tuser.login else f"{login}"
				embed.add_field(name="트위치", value=f"{twitchName}", inline=False)
			else:
				embed.add_field(name="트위치", value="[여기](https://c.ihah.me/s)를 눌러 연동을 진행하세요!", inline=False)
			if n[1]:
				embed.add_field(name="마인크래프트", value=f"{MCUUID(uuid=n[1]).name}\n`{n[1]}`", inline=False)
			else:
				embed.add_field(name="마인크래프트", value="[여기](https://c.ihah.me/login/minecraft)를 눌러 연동을 진행하세요!", inline=False)
			await i.response.send_message(embed=embed, ephemeral=True)
		else:
			embed = disnake.Embed(
				title="⚠️ 오류!",
				description=f"{user.mention}님에게 연동된 정보가 없습니다."
			)
			await i.response.send_message(embed=embed, ephemeral=True)

def setup(bot: commands.Bot):
	bot.add_cog(Management(bot))