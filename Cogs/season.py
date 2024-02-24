import disnake, sqlite3
from disnake.ext import commands
from config import SEASON, SEASON_TEXT
from modules.embed import makeErrorEmbed
from modules.exp import expNow
from modules.inventory import addInventoryItem, createInventory, deleteInventory
from modules.item import getItemFull, getItemName, getItemEmoji
from modules.spass import getUserPremium, getUserRewarded, seasonPassReward, seasonPassRewardOptions, addUserRewarded

class SeasonPassRewardCheckingView(disnake.ui.View):
	def __init__(
		self,
		itemLevel: int,
		itemNumber: int
	):
		self._itemLevel = itemLevel
		self._itemNumber = itemNumber
		super().__init__()
	
	@disnake.ui.button(emoji="✅", label="받기", style=disnake.ButtonStyle.green)
	async def yesRecieveReward(self, button: disnake.Button, i: disnake.Interaction):
		passItem = await seasonPassReward(level=self._itemLevel, itemNumber=self._itemNumber)
		try:
			await addInventoryItem(i.user.id, passItem[0], passItem[1], data=passItem[2])
		except sqlite3.OperationalError as e:
			if 'no such table' in f'{e}':
				await createInventory(i.user)
				await addInventoryItem(i.user.id, passItem[0], passItem[1], data=passItem[2])
			if 'no such column' in f'{e}':
				await deleteInventory(i.user)
				await createInventory(i.user)
				await addInventoryItem(i.user.id, passItem[0], passItem[1], data=passItem[2])
			else:
				pass
		await addUserRewarded(i.user.id, self._itemLevel, self._itemNumber, 1)
		embed = disnake.Embed(
			title=f"✅ 채팅패스 보상 받기 완료!",
			description=f"{await getItemEmoji(passItem[0])} **{await getItemName(passItem[0], i.locale)}** ×`{'{:,}'.format(passItem[1])}`",
			color=0x00ff00
		)
		[options, nextPage] = await seasonPassRewardOptions(user=i.user, locale=i.locale, premium=(await getUserPremium(i.user)))
		await i.response.edit_message(embed=embed, view=SeasonView(options, 1, nextPage))
		self.stop()
	
	@disnake.ui.button(emoji="❌", label="취소", style=disnake.ButtonStyle.grey)
	async def noRecieveReward(self, button: disnake.Button, i: disnake.Interaction):
		embed = disnake.Embed(
			title=f"{SEASON_TEXT} 시즌 보상",
			color=0xabcdef
		)
		[options, nextPage] = await seasonPassRewardOptions(user=i.user, locale=i.locale, premium=(await getUserPremium(i.user)))
		await i.response.edit_message(embed=embed, view=SeasonView(options, 1, nextPage))
		self.stop()

class SeasonSelect(disnake.ui.Select):
	def __init__(
		self,
		options: list[disnake.SelectOption]
	):
		super().__init__(placeholder="아직 받지 않은 보상", options=options)
	
	async def callback(self, i: disnake.Interaction):
		itemLevel = int(self.values[0].split("/")[0])
		itemNumber = int(self.values[0].split("/")[1])
		if itemNumber >= 4 and not await getUserPremium(i.user):
			await i.response.send_message(embed=makeErrorEmbed("채팅패스 프리미엄 전용 보상이에요."), ephemeral=True)
			return
		if (await expNow(i.user))[1] < itemLevel:
			await i.response.send_message(embed=makeErrorEmbed("아직 획득할 수 없는 보상이에요."), ephemeral=True)
			return
		if (await getUserRewarded(i.user.id, itemLevel, itemNumber)):
			await i.response.send_message(embed=makeErrorEmbed("이미 획득한 보상이에요."), ephemeral=True)
			return
		passItem = await seasonPassReward(level=itemLevel, itemNumber=itemNumber)
		embed = disnake.Embed(
			title="🎁 채팅패스 보상 받기",
			description=f"레벨 {itemLevel} 보상 #{itemNumber if itemNumber < 4 else 'Premium'}\n{await getItemEmoji(passItem[0])} **{await getItemName(passItem[0], i.locale)}** ×`{'{:,}'.format(passItem[1])}`",
			color=0xE67E22
		)
		await i.response.edit_message(embed=embed, view=SeasonPassRewardCheckingView(itemLevel=itemLevel, itemNumber=itemNumber))
		return

class SeasonLeftButton(disnake.ui.Button):
	def __init__(
		self,
		previousPage: int
	):
		super().__init__(emoji="◀️", style=disnake.ButtonStyle.gray, row=2, disabled=True if previousPage == 0 else False)
		self._previousPage = previousPage
	
	async def callback(self, i: disnake.Interaction):
		embed = disnake.Embed(
			title=f"{SEASON_TEXT} 시즌 보상",
			color=0xabcdef
		)
		[options, nextPage] = await seasonPassRewardOptions(user=i.user, locale=i.locale, premium=(await getUserPremium(i.user)), page=self._previousPage)
		await i.response.edit_message(embed=embed, view=SeasonView(options, self._previousPage, nextPage))
		return

class SeasonPageButton(disnake.ui.Button):
	def __init__(
		self,
		nowPage: int
	):
		super().__init__(label=f"Page {nowPage}", style=disnake.ButtonStyle.primary, row=2, disabled=True)

class SeasonRightButton(disnake.ui.Button):
	def __init__(
		self,
		nextPage: int,
		nextBoolean: bool
	):
		super().__init__(emoji="▶️", style=disnake.ButtonStyle.gray, row=2, disabled=not nextBoolean)
		self._nextPage = nextPage
	
	async def callback(self, i: disnake.Interaction):
		embed = disnake.Embed(
			title=f"{SEASON_TEXT} 시즌 보상",
			color=0xabcdef
		)
		[options, nextPage] = await seasonPassRewardOptions(user=i.user, locale=i.locale, premium=(await getUserPremium(i.user)), page=self._nextPage)
		await i.response.edit_message(embed=embed, view=SeasonView(options, self._nextPage, nextPage))
		return

class SeasonView(disnake.ui.View):
	def __init__(
		self,
		options: list[disnake.SelectOption],
		nowPage: int,
		nextBoolean: bool
	):
		super().__init__()
		self.add_item(SeasonSelect(options))
		self.add_item(SeasonLeftButton(nowPage-1))
		self.add_item(SeasonPageButton(nowPage))
		self.add_item(SeasonRightButton(nowPage+1, nextBoolean))
	
	@disnake.ui.button(label="전체 받기", emoji="✅", style=disnake.ButtonStyle.green, row=3)
	async def recieveAllRewards(self, button: disnake.Button, i: disnake.Interaction):
		await i.response.defer(ephemeral=True)
		items = {}
		premium = getUserPremium(i.user)
		exp = await expNow(i.user)
		for level in range(0, exp[1]+2):
			for x in range(1, 5):
				passItem = await seasonPassReward(level=level, itemNumber=x)
				if passItem and passItem[0]:
					optionAppend = True
					if (await getUserRewarded(i.user.id, level, x)):
						optionAppend = False
					if x == 4 and not premium:
						optionAppend = False
					if optionAppend:
						try:
							await addInventoryItem(i.user.id, passItem[0], passItem[1], data=passItem[2])
						except sqlite3.OperationalError as e:
							if 'no such column' in f'{e}':
								await deleteInventory(i.user)
							if 'no such table' in f'{e}':
								await createInventory(i.user)
								await addInventoryItem(i.user.id, passItem[0], passItem[1], data=passItem[2])
							else:
								pass
						await addUserRewarded(i.user.id, level, x, 1)
						# options.append(
						# 	disnake.SelectOption(
						# 		label=f"레벨 {level} 보상 #{x if x < 4 else 'Premium'} {emoji}",
						# 		description=f"{await getItemName(item=passItem[0], locale=i.locale)}×{passItem[1]}",
						# 		value=f"{level}/{x}",
						# 		emoji=(await getItemEmoji(item=passItem[0]))
						# 	)
						# )
						if passItem[0] in items: items[passItem[0]] += passItem[1]
						else: items[passItem[0]] = passItem[1]
		embed = disnake.Embed(
			title="✅ 전체 받기 완료!",
			color=0x00ff00,
			description='\n'.join([f"{await getItemFull(item=x, locale=i.locale)} `×{items[x]}`" for x in items])
		)
		await i.edit_original_message(embed=embed)

class Season(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.slash_command(
		name=disnake.Localized(
			"pass",
			data={
				disnake.Locale.ko: "채팅패스"
			}
		),
		description=disnake.Localized(
			"Check [Chatting Pass] season rewards.",
			data={
				disnake.Locale.ko: "채팅 패스 시즌 보상을 확인해요."
			}
		),
		options=[
			disnake.Option(
				name=disnake.Localized(
					"season",
					data={
						disnake.Locale.ko: "시즌"
					}
				),
				description=disnake.Localized(
					"Season name.",
					data={
						disnake.Locale.ko: "시즌 이름."
					}
				),
				type=disnake.OptionType.string,
				autocomplete=True
			)
		]
	)
	async def seasonPassRewardsSlashCommands(
		self,
		i: disnake.CommandInteraction,
		season: str = None
	):
		if not season:
			season = SEASON
		try:
			[options, nextPage] = await seasonPassRewardOptions(user=i.user, locale=i.locale, premium=(await getUserPremium(i.user)), page=1)
			if len(options) > 0:
				embed = disnake.Embed(
					title=f"{SEASON_TEXT} 시즌 보상",
					color=0xabcdef
				)
				await i.response.send_message(embed=embed, view=SeasonView(options, 1, nextPage), ephemeral=True)
			else:
				await i.response.send_message(embed=makeErrorEmbed("받을 보상이 남아있지 않아요."))
		except Exception as e:
			print(e)
			await i.response.send_message(embed=makeErrorEmbed(f"서버 내 오류가 발생했어요...\n```{e}```"), ephemeral=True)

	@seasonPassRewardsSlashCommands.autocomplete("season")
	def getSeasonNames(self, i: disnake.CommandInteraction, search: str):
		conn = sqlite3.connect('season.db', isolation_level=None)
		c = conn.cursor()
		c.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table', 'view') ORDER BY 1;")
		n = c.fetchall()
		seasons = []
		for x in n:
			seasons.append(x[0])
		return seasons
	
def setup(bot: commands.Bot):
	bot.add_cog(Season(bot))