import disnake, sqlite3, time
from config import SEASON
from modules.embed import makeErrorEmbed
from ..item import getItemName
from ..inventory import getInventoryItemAmount, removeInventoryItem

async def useExpBottle(user: disnake.Member, data: dict):
	conn = sqlite3.connect("user.db", isolation_level=None)
	c = conn.cursor()
	bottlePeriod = time.time() + data['minutes'] * 60
	c.execute(f"UPDATE '{SEASON}' SET bottleMultiple={data['multiple']},bottlePeriod={bottlePeriod} WHERE userId={user.id}")
	await removeInventoryItem(user=user.id, item="exp-bottle", amount=1, data=f"{data}".replace("'", '"'))
	conn.close()

async def getExpBottle(user: disnake.Member) -> float:
	conn = sqlite3.connect("user.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT bottleMultiple,bottlePeriod FROM '{SEASON}' WHERE userId={user.id}")
	n = c.fetchone()
	conn.close()
	if n[1] > time.time():
		return n[0]-1
	else:
		return 0.0

class Item_ExpBottle_UseButton(disnake.ui.Button):
	def __init__(
		self,
		locale: disnake.Locale,
		option: dict
	):
		self._option = option
		super().__init__(style=disnake.ButtonStyle.green, label="사용하기" if locale == disnake.Locale.ko else "Use", emoji="🪄")
	
	async def callback(self, i:disnake.Interaction):
		if await getInventoryItemAmount(user=i.user.id, item=self._item) > 0:
			await useExpBottle(i.user, self._option)
			embed = disnake.Embed(
				title=f"🪄 {await getItemName(item='exp-bottle', locale=i.locale)}",
				description=f"경험치 성장의 물약을 마셨어요.\n꿀꺽! 목을 넘어가는게 심상치 않은데요?\n이제 {self._option['minutes']}분 동안 경험치를 {self._option['multiple']}배로 획득한답니다!"
			)
		else:
			embed = makeErrorEmbed("아이템이 부족해요.")
		await i.response.edit_message(embed=embed, view=None)

class Item_ExpBottle_Use(disnake.ui.View):
	def __init__(
		self,
		locale: disnake.Locale,
		option: str
	):
		super().__init__()
		self.add_item(Item_ExpBottle_UseButton(locale, option))