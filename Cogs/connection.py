import disnake, sqlite3, mcuuid
from disnake.ext import commands
from config import helix

class Connection(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
	
	@commands.slash_command(
		name=disnake.Localized(
			"connections",
			data={
				disnake.Locale.ko: "연동확인"
			}
		),
		description=disnake.Localized(
			"Check if it is linked with other accounts.",
			data={
				disnake.Locale.ko: "타 계정과 연동이 되었는지 확인합니다."
			}
		),
		guild_ids=[812664224512868382,742188157424107679]
	)
	async def twitch_discord(i: disnake.CommandInteraction):
		conn = sqlite3.connect('auth.db', isolation_level=None)
		c = conn.cursor()
		c.execute(f"select twitch,minecraft,epicstore from user where id={i.user.id}")
		n = c.fetchone()
		if n:
			user = helix.user(int(n[0]))
			embed = disnake.Embed(
				title="연동 정보 확인",
				description=f"{i.user.mention}님의 연동 정보입니다."
			)
			if n[0]:
				display_name = user.display_name.replace('_', '\_')
				login = user.login.replace('_', '\_')
				twitchName = f"{display_name}({login})" if user.display_name != user.login else f"{login}"
				embed.add_field(name="트위치", value=f"{twitchName}", inline=False)
			else:
				embed.add_field(name="트위치", value="[여기](https://c.ihah.me/s)를 눌러 연동을 진행하세요!", inline=False)
			if n[1]:
				embed.add_field(name="마인크래프트", value=f"{mcuuid.MCUUID(uuid=n[1]).name}\n`{n[1]}`", inline=False)
			else:
				embed.add_field(name="마인크래프트", value="[여기](https://c.ihah.me/login/minecraft)를 눌러 연동을 진행하세요!", inline=False)
			# if n[2]:
			# 	data = "grant_type=client_credentials&deployment_id=c636a7043b33471d93cf5f67f08e5831"
			# 	headers={
			# 		'Content-Type': 'application/x-www-form-urlencoded',
			# 		'Authorization': 'Basic eHl6YTc4OTE4N3o4bjJSdzVUOFFKQkVCTlZqd05QS2E6akZFSkUyYTVZSkJuU01KdWtZUllDMGJCZ01NbVJkUFVabHRmQ1NPU0h0bw=='
			# 	}
			# 	req = requests.post("https://api.epicgames.dev/epic/oauth/v1/token", data=data, headers=headers)
			# 	r = json.loads(req.text)
			# 	print(r)
			# 	headers = {
			# 		"Authroization": f"Bearer {r['access_token']}"
			# 	}
			# 	req = requests.get(f"https://api.epicgames.dev/user/v1/product-users?productUserId={n[2]}", headers=headers)
			# 	print(req.text)
			# 	r = json.loads(req.text)
			# 	print(r)
			# 	embed.add_field(name="에픽게임즈", value="1", inline=False)
			# else:
			# 	embed.add_field(name="에픽게임즈", value="[여기](https://c.ihah.me/login/epicstore)를 눌러 연동을 진행하세요!", inline=False)
			# embed.add_field(name="스팀", value="준비중입니다!", inline=False)
			await i.response.send_message(embed=embed)
		else:
			embed = disnake.Embed(
				title="⚠️ 오류!",
				description="연동된 정보가 없습니다."
			)
			await i.response.send_message(embed=embed)

def setup(bot: commands.Bot):
	bot.add_cog(Connection(bot))