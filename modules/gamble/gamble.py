import disnake, sqlite3
from ..embed import makeErrorEmbed
from ..inventory import getInventoryItemAmount

async def gamble_moneyLimit(i: disnake.CommandInteraction, betting):
	if betting < 100:
		await i.response.send_message(embed=makeErrorEmbed("냥코인은 최소 100부터 입력해야 해요."), ephemeral=True)
		return True
	meowCoin = await getInventoryItemAmount(user=i.user.id, item="meow-coin")
	if meowCoin < betting:
		await i.response.send_message(embed=makeErrorEmbed("냥코인이 부족해요."), ephemeral=True)
		return True
	if betting > 50000:
		await i.response.send_message(embed=makeErrorEmbed("최대 베팅 가능 냥코인을 넘었어요. (`50,000`)"), ephemeral=True)
		return True
	return False

def gamble_executeSQL(sql: str):
	conn = sqlite3.connect("gamble.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"{sql}")
	result = None
	if sql.startswith("SELECT"):
		result = c.fetchall()
		if len(result) == 1: result = result[0]
		if len(result) == 1: result = result[0]
	conn.close()
	return result