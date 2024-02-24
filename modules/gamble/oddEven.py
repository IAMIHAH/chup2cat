import disnake, random
from .gamble import gamble_moneyLimit
from ..embed import makeErrorEmbed
from ..inventory import addInventoryItem, removeInventoryItem

class gamble_oddEven_View(disnake.ui.View):
	def __init__(
		self,
		userId: int,
		guess: int,
		betting: int
	):
		self._userId = userId
		self._guess = guess
		self._betting = betting
		super().__init__(timeout=180)
		
	@disnake.ui.button(label="확인하기", style=disnake.ButtonStyle.green)
	async def checkResult(self, button: disnake.Button, i: disnake.Interaction):
		if i.user.id != self._userId:
			await i.response.send_message(embed=makeErrorEmbed("선택권은 메시지 주인에게 있어요!"), ephemeral=True)
			return
		number = random.randint(1, 100)
		if self._guess == number%2:
			result = ['성공!', f"`{'{:,}'.format(self._betting)}` 냥코인을 얻었어요."]
			await addInventoryItem(user=i.user.id, item="meow-coin", amount=self._betting)
		else:
			result = ['실패...', f"`{'{:,}'.format(self._betting)}` 냥코인을 잃었어요."]
			await removeInventoryItem(user=i.user.id, item="meow-coin", amount=self._betting)
		embed = disnake.Embed(
			title="🎲 홀짝!"
		)
		embed.add_field(name="추측", value=f"{'홀수' if self._guess == 1 else '짝수'}")
		embed.add_field(name="결과", value=f"`{number}` → {'홀수' if number%2 == 1 else '짝수'}")
		embed.add_field(name=f"{result[0]}", value=f"{result[1]}")
		await i.response.edit_message(content=None, embed=embed, view=None)
		
	@disnake.ui.button(label="취소", style=disnake.ButtonStyle.grey)
	async def cancelButton(self, button: disnake.Button, i: disnake.Interaction):
		if i.user.id != self._userId:
			await i.response.send_message(embed=makeErrorEmbed("선택권은 메시지 주인에게 있어요!"), ephemeral=True)
			return
		await i.response.edit_message(content="*(만료된 상호작용입니다.)*", embed=None, view=None)

async def oddeven_start(i: disnake.CommandInteraction, betting: int, guess: int):
	if await gamble_moneyLimit(i, betting):
		return
	embed = disnake.Embed(
		title="🎲 홀짝!",
		description=f"정답은..."
	)
	embed.add_field(name="추측", value=f"{'홀수' if guess == 1 else '짝수'}")
	embed.set_footer(text="결과를 확인할 때까지 냥코인이 줄어들지 않아요.")
	await i.response.send_message(embed=embed, view=gamble_oddEven_View(i.user.id, guess, betting))