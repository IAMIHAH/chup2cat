import json
import disnake, sqlite3
from disnake.ext import commands
from modules.embed import makeErrorEmbed, makeInventoryItemEmbed
from modules.item import getItemEmoji, getItemName
from modules.inventory import createInventory, deleteInventory, getAllInventoryItems, getInventoryItemAmount
from modules.inventoryEmbed import makeInventoryItemEmbedView

class InventorySelect(disnake.ui.Select):
	def __init__(
		self,
		user: disnake.Member,
		inventoryItems: list[disnake.SelectOption]
	):
		self._user = user
		super().__init__(custom_id=f"inv-{user.id}", placeholder="보유중인 아이템", options=inventoryItems)
	
	async def callback(self, i: disnake.Interaction):
		if self._user.id != i.user.id:
			await i.response.send_message(embed=makeErrorEmbed("선택권은 메시지 주인에게 있어요!"), ephemeral=True)
			return
		itemId = self.values[0].split("@@")[0].split("$$")[0]
		itemAmount = int(self.values[0].split("@@")[0].split("$$")[1])
		if itemAmount > 0:
			[embed, view] = await makeInventoryItemEmbedView(i, itemId,self.values[0].split("@@")[1])
			if not embed: await i.response.send_message(embed=makeErrorEmbed("그런 아이템을 가지고 있지 않아요!"), ephemeral=True)
			await i.response.send_message(embed=embed, view=view, ephemeral=True)
		else:
			await i.response.send_message(embed=makeErrorEmbed("그런 아이템을 가지고 있지 않아요!"), ephemeral=True)

class InventoryView(disnake.ui.View):
	def __init__(
		self,
		user: disnake.Member,
		inventoryItems: list[disnake.SelectOption]
	):
		super().__init__(timeout=180)
		self.add_item(InventorySelect(user=user, inventoryItems=inventoryItems))

class Inventory(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.slash_command(
		name=disnake.Localized(
			"inventory",
			data={
				disnake.Locale.ko: "인벤토리"
			}
		),
		description=disnake.Localized(
			"Check your inventory.",
			data={
				disnake.Locale.ko: "인벤토리를 확인해요."
			}
		),
		options=[
			disnake.Option(
				name="user",
				description="유저명 (관리자전용)",
				type=disnake.OptionType.user
			)
		],
		guild_ids=[812664224512868382,742188157424107679]
	)
	async def userInventory(
		self,
		i: disnake.CommandInteraction,
		user: disnake.Member=None
	):
		if user and not i.user.guild_permissions.administrator: user = i.user
		if not user: user = i.user
		embed = disnake.Embed(
			title="💼 내 인벤토리"
		)
		try:
			meowCoin = await getInventoryItemAmount(user=user.id, item="meow-coin")
		except sqlite3.OperationalError as e:
			if 'no such table' in f'{e}':
				await createInventory(user)
			if 'no such column' in f'{e}':
				await deleteInventory(user)
				await createInventory(user)
			meowCoin = await getInventoryItemAmount(user=user.id, item="meow-coin")
		embed.add_field(name="🪙 냥코인", value=f"`{'{:,}'.format(meowCoin)}`")
		crystal = await getInventoryItemAmount(user=user.id, item="crystal")
		embed.add_field(name="💎 크리스탈", value=f"`{'{:,}'.format(crystal)}`")
		items = await getAllInventoryItems(user=user.id)
		inventoryItems = []
		for x in items:
			if x[1] > 0:
				if x[0] != "meow-coin" and x[0] != "crystal":
					emoji = await getItemEmoji(x[0])
					inventoryItems.append(
						disnake.SelectOption(
							label=f"{await getItemName(x[0], i.locale)}",
							value=f"{x[0]}$${x[1]}@@{x[2]}",
							description=f"×{x[1]}",
							emoji=f"{emoji}" if emoji else "🔘"
						)
					)
		if len(inventoryItems) > 0:
			await i.response.send_message(embed=embed, view=InventoryView(user=user, inventoryItems=inventoryItems))
		else:
			await i.response.send_message(embed=embed)

def setup(bot: commands.Bot):
	bot.add_cog(Inventory(bot))