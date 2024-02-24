import disnake, random
from ..embed import makeErrorEmbed, makeInventoryItemEmbed
from ..message import numberJosa
from ..item import getItemFull, getItemName
from ..inventory import addInventoryItem, getInventoryItemAmount, removeInventoryItem

class Item_Lottery_UseButton(disnake.ui.Button):
	def __init__(
		self,
		locale: disnake.Locale,
		item
	):
		self._item = item
		super().__init__(style=disnake.ButtonStyle.green, label='사용하기' if locale == disnake.Locale.ko else 'Use', emoji="🪄")
	
	async def callback(self, i:disnake.Interaction):
		if await getInventoryItemAmount(user=i.user.id, item=self._item) > 0:
			amount = 0
			if self._item == "lottery": amount = random.randint(100, 300)
			if self._item == "lottery-gold": amount = random.randint(500, 1000)
			await removeInventoryItem(user=i.user.id, item=self._item, amount=1)
			await addInventoryItem(user=i.user.id, item="meow-coin", amount=amount)
			embed = disnake.Embed(
				title=f"🪄 {await getItemName(item=self._item, locale=i.locale)} {'사용하기' if i.locale == disnake.Locale.ko else 'Use'}",
				description=f"[ {await getItemFull(item=self._item, locale=i.locale)} ] 을 긁어 [ {await getItemFull(item='meow-coin', locale=i.locale)} ] `×{amount}`{numberJosa(amount)} 획득했어요!"
			)
			await i.channel.send(content=f"{i.user.mention}", embed=embed)

			embed = await makeInventoryItemEmbed(i, self._item)
			if embed: await i.response.edit_message(embed=embed)
			else: await i.response.edit_message(content="*(만료된 상호작용입니다.)*", embed=None, view=None)
		else:
			await i.response.send_message(embed=makeErrorEmbed("아이템이 부족해요."), ephemeral=True)
		return

class Item_Lottery_UseButton_10(disnake.ui.Button):
	def __init__(
		self,
		locale: disnake.Locale,
		item
	):
		self._item = item
		super().__init__(style=disnake.ButtonStyle.green, label='10회 사용하기' if locale == disnake.Locale.ko else 'Use', emoji="🪄")
	
	async def callback(self, i:disnake.Interaction):
		itemAmount = await getInventoryItemAmount(user=i.user.id, item=self._item)
		if itemAmount > 0:
			itemFull = await getItemFull(item=self._item, locale=i.locale)
			itemFullCoin = await getItemFull(item="meow-coin", locale=i.locale)
			if itemAmount > 10: itemAmount = 10
			description = [f"{itemFull}을 `{itemAmount}`개 사용했어요!"]
			amount = 0
			for x in range(itemAmount):
				if self._item == "lottery":
					am = random.randint(100, 300)
				if self._item == "lottery-gold":
					am = random.randint(500, 1000)
				amount += am
				description.append(f"[ {itemFull} ] 을 긁어 [ {itemFullCoin} ] `×{am}`{numberJosa(am)} 획득했어요!")
			if itemAmount < 10: description.append(f"사용하려다 문제가 생겼어요: 아이템이 부족해요.")
			await removeInventoryItem(user=i.user.id, item=self._item, amount=itemAmount)
			await addInventoryItem(user=i.user.id, item="meow-coin", amount=amount)
			embed = disnake.Embed(
				title=f"🪄 {await getItemName(item=self._item, locale=i.locale)} {'사용하기' if i.locale == disnake.Locale.ko else 'Use'}",
				description='\n'.join(description)
			)
			await i.channel.send(content=f"{i.user.mention}", embed=embed)

			embed = await makeInventoryItemEmbed(i, self._item)
			if embed: await i.response.edit_message(embed=embed)
			else: await i.response.edit_message(content="*(만료된 상호작용입니다.)*", embed=None, view=None)
		else:
			await i.response.send_message(embed=makeErrorEmbed("아이템이 부족해요."), ephemeral=True)
		return

class Item_Lottery_Use(disnake.ui.View):
	def __init__(
		self,
		locale: disnake.Locale,
		item: str
	):
		super().__init__()
		self.add_item(Item_Lottery_UseButton(locale, item))
		self.add_item(Item_Lottery_UseButton_10(locale, item))