import disnake
def makeErrorEmbed(desc: str): return disnake.Embed(title=":warning: 오류!", description=desc, color=0xff0000)

from .inventory import getInventoryItemAmount
from .item import getItemDesc, getItemName, getItemEmoji
async def makeInventoryItemEmbed(i: disnake.Interaction, itemId: str, itemData: str=None):
	itemAmount = await getInventoryItemAmount(i.user.id, itemId, itemData)
	emoji = await getItemEmoji(itemId)
	r = itemData
	if itemAmount > 0:
		emoji = await getItemEmoji(itemId)
		embed = disnake.Embed(
			title=f"{emoji if emoji else '🔘'} {await getItemName(itemId, i.locale)}",
			description=f"{await getItemDesc(itemId, i.locale)}"
		)
		embed.add_field(name="보유 개수", value=f"`{itemAmount}`")
		if itemId == "exp-bottle":
			embed.add_field(name="배수", value=f"{r['multiple']}배")
			embed.add_field(name="기간", value=f"{r['minutes']}분")
		return embed
	else:
		return None