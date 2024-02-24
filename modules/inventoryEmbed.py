import disnake, json
from .items.expbottle import Item_ExpBottle_Use
from .items.lottery import Item_Lottery_Use
from .inventory import getInventoryItemAmount
from .item import getItemDesc, getItemName, getItemEmoji

async def makeInventoryItemEmbedView(i: disnake.Interaction, itemId: str, itemData: dict=None):
	itemAmount = await getInventoryItemAmount(i.user.id, itemId, itemData)
	if itemAmount <= 0: return [None, None]
	r = json.loads(itemData)
	emoji = await getItemEmoji(itemId)

	embed = disnake.Embed(
		title=f"{emoji if emoji else '🔘'} {await getItemName(itemId, i.locale)}",
		description=f"{await getItemDesc(itemId, i.locale)}"
	)
	embed.add_field(name="보유 개수", value=f"`{itemAmount}`")
	if itemId == "exp-bottle":
		embed.add_field(name="배수", value=f"{r['multiple']}배")
		embed.add_field(name="기간", value=f"{r['minutes']}분")
		return [embed, Item_ExpBottle_Use(i.locale, r)]
	elif itemId == "lottery" or itemId == "lottery-gold":
		return [embed, Item_Lottery_Use(i.locale, itemId)]
	return [embed, None]