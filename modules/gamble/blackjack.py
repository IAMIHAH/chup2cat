import disnake, sqlite3, json, random
from .gamble import gamble_executeSQL, gamble_moneyLimit
from ..embed import makeErrorEmbed
from ..inventory import addInventoryItem, removeInventoryItem

class blackjackView(disnake.ui.View):
	doubleDownButtonDisplay = True

	def __init__(
		self,
		userId: int,
		doubleDown: bool = True
	):
		self._userId = userId
		self.doubleDownButtonDisplay = doubleDown
		super().__init__(timeout=None)

	async def playerTurn(self, i: disnake.Interaction, cards: list):
		card : list = blackjack_getCards(i.user.id, "player", False)
		card.append(cards.pop(random.randint(0, len(cards)-1)))
		blackjack_setCards(i.user.id, "player", card)
		return cards

	async def dealerTurn(self, i: disnake.Interaction, cards: list, doubleDown: bool=False):
		card : list = blackjack_getCards(i.user.id, "dealer", False)
		cardAdd = False
		if doubleDown:
			await i.channel.send("첩첩냥: 카드 +1 (더블 다운)")
			cardAdd = True
		else:
			[cardMin, cardMax] = blackjack_cardTranslate(i.user.id, 'dealer', False)
			if cardMin < 17 or cardMax < 17:
				await i.channel.send("첩첩냥: 힛 - 카드 +1")
				cardAdd = True
			else:
				await i.channel.send("첩첩냥: 스탠드")
		if cardAdd:
			card.append(cards.pop(random.randint(0, len(cards)-1)))
			blackjack_setCards(i.user.id, "dealer", card)
		return [cards, cardAdd]


	@disnake.ui.button(label="힛", style=disnake.ButtonStyle.green)
	async def buttonHit(self, button: disnake.Button, i: disnake.Interaction):
		if i.user.id != self._userId:
			await i.response.send_message(embed=makeErrorEmbed("선택권은 메시지 주인에게 있어요!"), ephemeral=True)
			return
		await i.channel.send(f"{i.user.name}: 힛 - 카드 +1")
		cards : list = blackjack_getCards(i.user.id, "remained", False)
		cards = await self.playerTurn(i, cards)
		[cards, cardAdd] = await self.dealerTurn(i, cards)
		blackjack_setCards(i.user.id, "remained", cards)
		await i.response.edit_message(content="", view=None)
		embed = await blackjack_makeEmbed(i.user, blackjack_getBetting(i.user.id), i.channel)
		if embed: await i.channel.send(embed=embed, view=blackjackView(i.user.id, self.doubleDownButtonDisplay))
		return

	@disnake.ui.button(label="스탠드", style=disnake.ButtonStyle.gray)
	async def buttonStand(self, button: disnake.Button, i: disnake.Interaction):
		if i.user.id != self._userId:
			await i.response.send_message(embed=makeErrorEmbed("선택권은 메시지 주인에게 있어요!"), ephemeral=True)
			return
		await i.channel.send(f"{i.user.name}: 스탠드")
		cards : list = blackjack_getCards(i.user.id, "remained", False)
		[cards, cardAdd] = await self.dealerTurn(i, cards)
		blackjack_setCards(i.user.id, "remained", cards)
		await i.response.edit_message(content="", view=None)
		if not cardAdd:
			await blackjack_gameEnd(i.user, i.channel, True)
			return
		embed = await blackjack_makeEmbed(i.user, blackjack_getBetting(i.user.id), i.channel)
		if embed: await i.channel.send(embed=embed, view=blackjackView(i.user.id, self.doubleDownButtonDisplay))
		return

	@disnake.ui.button(label="더블 다운", style=disnake.ButtonStyle.blurple, disabled=(not doubleDownButtonDisplay))
	async def buttonDoubleDown(self, button: disnake.Button, i: disnake.Interaction):
		if i.user.id != self._userId:
			await i.response.send_message(embed=makeErrorEmbed("선택권은 메시지 주인에게 있어요!"), ephemeral=True)
			return
		betting = blackjack_getBetting(i.user.id)
		if await gamble_moneyLimit(i, betting*2):
			await i.response.send_message(embed=makeErrorEmbed("냥코인이 부족해요."))
			return
		gamble_executeSQL(f'UPDATE blackjack SET betting={betting*2} WHERE userId={i.user.id}')
		await i.channel.send(f"{i.user.name}: 더블 다운 - 베팅액 2배, 카드 +1")
		cards : list = blackjack_getCards(i.user.id, "remained", False)
		cards = await self.playerTurn(i, cards)
		[cards, cardAdd] = await self.dealerTurn(i, cards, True)
		blackjack_setCards(i.user.id, "remained", cards)
		await i.response.edit_message(content="", view=None)
		embed = await blackjack_makeEmbed(i.user, blackjack_getBetting(i.user.id), i.channel)
		if embed: await i.channel.send(embed=embed, view=blackjackView(i.user.id, self.doubleDownButtonDisplay))
		return

	@disnake.ui.button(label="서렌더", style=disnake.ButtonStyle.red)
	async def buttonSurrender(self, button: disnake.Button, i: disnake.Interaction):
		if i.user.id != self._userId:
			await i.response.send_message(embed=makeErrorEmbed("선택권은 메시지 주인에게 있어요!"), ephemeral=True)
			return
		betting = blackjack_getBetting(i.user.id)
		await i.response.edit_message(content="", view=None)
		await blackjack_gameEnd(i.user, i.channel, win=0, half=True)
		embed = disnake.Embed(
			title=f"👑 {i.user.name} 서렌더!",
			description=f"`{round(betting*0.5)}` 냥코인을 받습니다."
		)
		await i.channel.send(f"{i.user.name}: 서렌더 - 게임 종료, 베팅 금액 절반 획득", embed=embed)
		return
	
	@disnake.ui.button(label="블랙잭?", emoji="❓", style=disnake.ButtonStyle.link, url="https://namu.wiki/w/블랙잭(카드게임)")
	async def buttonHowToPlay(self, button: disnake.Button, i: disnake.Interaction):
		return

async def blackjack_gameEnd(user: disnake.Member, ch: disnake.Thread, stand: bool=False, win: int=0, half: bool=False):
	betting = blackjack_getBetting(user.id)
	if stand:
		[playerCardMin, playerCardMax] = blackjack_cardTranslate(user.id, 'player')
		[dealerCardMin, dealerCardMax] = blackjack_cardTranslate(user.id, 'dealer', False)
		playerCard = 0
		if playerCardMin == playerCardMax: playerCard = playerCardMin
		else:
			if playerCardMax > 21: playerCard = playerCardMin
			else: playerCard = playerCardMax
		dealerCard = 0
		if dealerCardMin == dealerCardMax: dealerCard = dealerCardMin
		else:
			if dealerCardMax > 21: dealerCard = dealerCardMin
			else: dealerCard = dealerCardMax
		if playerCard == dealerCard:
			embed = disnake.Embed(title=f"👑 푸시, 무승부!")
			win = 2
		else:
			if playerCard > dealerCard:
				embed = disnake.Embed(
					title=f"👑 {user.name} 승리!",
					description=f"`{blackjack_getBetting(user.id)}` 냥코인을 받습니다."
				)
				win = 1
			else:
				embed = disnake.Embed(
					title=f"👑 첩첩냥 승리!",
					description=f"`{blackjack_getBetting(user.id)}` 냥코인을 잃습니다."
				)
				win = 0
		await blackjack_gameEnd(user=user, ch=ch, win=win)
		await ch.send(embed=embed)
		return
	else:
		color = 0x00ff00 if win == 1 else 0xff0000
		if win == 2: color = 0xabcdef
		embed = disnake.Embed(
			title="게임 종료!", color=color,
			description=f"🪙 `{'+' if win else '-'}{'{:,}'.format(betting if not half else round(betting*0.5))}`" if win != 2 else "🪙 `+0`"
		)
		cards = blackjack_getCards(user.id, "player")
		[cardMin, cardMax] = blackjack_cardTranslate(user.id, 'player')
		embed.add_field(
			name=f"[P] {f'{user.name[:10]}...' if len(user.name) > 10 else user.name} ({cardMin if cardMin == cardMax or cardMax > 21 else f'{cardMin}/{cardMax}'})",
			value=f"{cards}", inline=False
		)
		cards = blackjack_getCards(user.id, "dealer", dealerCardNotOpen=False)
		[cardMin, cardMax] = blackjack_cardTranslate(user.id, 'dealer', False)
		embed.add_field(
			name=f"[D] 첩첩냥 ({f'{cardMin}' if cardMin == cardMax or cardMax > 21 else f'{cardMin}/{cardMax}'})",
			value=f"{cards}", inline=False
		)
		await ch.send(embed=embed)
		if win == 1:
			await addInventoryItem(user.id, "meow-coin", betting if not half else round(betting*0.5))
		elif win == 0:
			await removeInventoryItem(user.id, "meow-coin", betting if not half else round(betting*0.5))
	gamble_executeSQL(f"DELETE FROM blackjack WHERE userId={user.id}")
	return

def blackjack_getBetting(userId: int):
	return int(gamble_executeSQL(f"SELECT betting FROM blackjack WHERE userId={userId}"))

def blackjack_getCards(userId: int, user: str, emote: bool=True, dealerCardNotOpen: bool = True):
	if user != "player" and user != "dealer" and user != "remained":
		return False
	emojis = [":a:",":two:",":three:",":four:",":five:",":six:",":seven:",":eight:",":nine:",":keycap_ten:",":regional_indicator_j:",":regional_indicator_q:",":regional_indicator_k:"]
	shape  = ["♠️","♣️","♥️","♦️"]
	shapes = [":spades:", ":clubs:",":hearts:", ":diamonds:"]
	cards = gamble_executeSQL(f"SELECT {user} FROM blackjack WHERE userId={userId}")
	cards = json.loads(str(cards).replace("'", '"'))
	if emote:
		result = []
		cardCount = 0
		for x in cards:
			cardCount += 1
			if cardCount == 1 and user == "dealer" and dealerCardNotOpen:
				result.append(f":grey_question::zero:")
			else:
				card = str(x).split(" ")
				for i in range(0, 4):
					if shape[i] == card[0]: card[0] = shapes[i]
				card[1] = emojis[int(card[1])-1]
				result.append(f"{card[0]}{card[1]}")
		return f"[{'] ['.join(result)}]"
	else:
		return cards

def blackjack_setCards(userId: int, user: str, cards: list):
	if user != "player" and user != "dealer" and user != "remained":
		return False
	gamble_executeSQL(f'UPDATE blackjack SET {user}="{str(cards)}" WHERE userId={userId}')

def blackjack_cardTranslate(userId: int, user: str, dealerCardNotOpen: bool = True):
	if user != "player" and user != "dealer":
		return False
	cards = json.loads(str(gamble_executeSQL(f"SELECT {user} FROM blackjack WHERE userId={userId}")).replace("'", '"'))
	cardCount = 0
	result = 0
	result2 = 0
	for x in cards:
		cardCount += 1
		if cardCount == 1 and user == "dealer" and dealerCardNotOpen:
			result += 0
		else:
			card = str(x).split(" ")
			if int(card[1]) == 1: result2 += 1
			if int(card[1]) >= 10:  result += 10
			else: result += int(card[1])
	if result2 > 0:
		return [result, result+10*result2]
	else:
		return [result, result]

def blackjack_checkBurst(userId: int, user: str):
	if user != "player" and user != "dealer":
		return False
	cards = json.loads(str(gamble_executeSQL(f"SELECT {user} FROM blackjack WHERE userId={userId}")).replace("'", '"'))
	result = 0
	for x in cards:
		card = str(x).split(" ")
		if int(card[1]) >= 10: 
			result += 10
		else:
			result += int(card[1])
	if result > 21:
		return True
	else:
		return False

async def blackjack_makeEmbed(user: disnake.Member, betting: int, ch: disnake.Thread, first: bool=False):
	embed = disnake.Embed(
		title="♠️ 블랙잭",
		description=f"🪙 `{'{:,}'.format(betting)}`"
	)
	blackjack = 0
	burst = 0
	cards = blackjack_getCards(user.id, "player")
	[cardMin, cardMax] = blackjack_cardTranslate(user.id, 'player')
	if cardMin == 21 or cardMax == 21:
		blackjack += 1
	if blackjack_checkBurst(user.id, 'player'):
		burst += 1
	embed.add_field(
		name=f"[P] {f'{user.name[:10]}...' if len(user.name) > 10 else user.name} ({cardMin if cardMin == cardMax or cardMax > 21 else f'{cardMin}/{cardMax}'})",
		value=f"{cards}", inline=False
	)
	cards = blackjack_getCards(user.id, "dealer")
	[cardMin, cardMax] = blackjack_cardTranslate(user.id, 'dealer')
	if cardMin == 21 or cardMax == 21:
		blackjack += 2
	if blackjack_checkBurst(user.id, 'dealer'):
		burst += 2
	embed.add_field(
		name=f"[D] 첩첩냥 ({f'{cardMin}+@' if cardMin == cardMax or cardMax > 21 else f'{cardMin}+@/{cardMax}+@'})",
		value=f"{cards}", inline=False
	)
	embed.set_footer(text="획득하는 냥코인은 원금을 제외합니다.")
	msg = ""
	win = 0
	if blackjack > 0:
		if first:
			if blackjack >= 3:
				msg = f"{user.name}: 블랙잭 - A + 10 = 21\n첩첩냥: 블랙잭 - A + 10 = 21"
				embed = disnake.Embed(title=f"👑 푸시, 무승부!")
				win = 2
			else:
				if blackjack >= 2:
					msg = "첩첩냥: 블랙잭 - A + 10 = 21"
					win = 0
					embed = disnake.Embed(
						title=f"👑 첩첩냥 블랙잭 승리!",
						description=f"`{round(betting*0.5)}` 냥코인을 잃습니다."
					)
				else:
					msg = f"{user.name}: 블랙잭 - A + 10 = 21"
					win = 1
					embed = disnake.Embed(
						title=f"👑 {user.name} 블랙잭 승리!",
						description=f"`{round(betting*0.5)}` 냥코인을 받습니다."
					)
				await blackjack_gameEnd(user, ch, win=win, half=True)
		else:
			if blackjack >= 3:
				msg = f"{user.name}: 21\n첩첩냥: 21"
				embed = disnake.Embed(title=f"👑 푸시, 무승부!")
				win = 2
			else:
				if blackjack >= 2:
					msg = "첩첩냥: 21"
					win = 0
					embed = disnake.Embed(
						title=f"👑 첩첩냥 승리!",
						description=f"`{betting}` 냥코인을 잃습니다."
					)
				else:
					msg = f"{user.name}: 21"
					win = 1
					embed = disnake.Embed(
						title=f"👑 {user.name} 승리!",
						description=f"`{betting}` 냥코인을 받습니다."
					)
				await blackjack_gameEnd(user, ch, win=win)
		await ch.send(content=msg, embed=embed)
		return False
	if burst > 0:
		if burst >= 3:
			msg = f"{user.name}: 버스트 - 카드 총합이 21을 넘음\n첩첩냥: 버스트 - 카드 총합이 21을 넘음"
			embed = disnake.Embed(title=f"👑 푸시, 무승부!")
			win = 2
		else:
			if burst >= 2:
				msg = f"첩첩냥: 버스트 - 카드 총합이 21을 넘음"
				win = 1
				embed = disnake.Embed(
					title=f"👑 {user.name} 승리!",
					description=f"`{betting}` 냥코인을 받습니다."
				)
			else:
				msg = f"{user.name}: 버스트 - 카드 총합이 21을 넘음"
				win = 0
				embed = disnake.Embed(
					title=f"👑 첩첩냥 승리!",
					description=f"`{betting}` 냥코인을 잃습니다."
				)
		await blackjack_gameEnd(user, ch, win=win)
		await ch.send(content=msg, embed=embed)
		return False
	return embed

async def blackjack_start(i: disnake.CommandInteraction, betting: int):
	if await gamble_moneyLimit(i, betting):
		return
	doubleDown = True
	if await gamble_moneyLimit(i, betting*2):
		doubleDown = False
	await i.response.defer(ephemeral=True)
	ch : disnake.Thread = await i.channel.create_thread(
		name=f"{f'{i.user.name[:10]}...' if len(i.user.name) > 10 else i.user.name}님의 블랙잭",
		message=None,
		type=disnake.ChannelType.public_thread
	)
	gamble_executeSQL(f"INSERT INTO blackjack(userId, channelId, betting) VALUES({i.user.id}, {ch.id}, {betting})")
	cards = []
	for shape in ["♠️","♣️","♥️","♦️"]:
		for x in range(1, 14):
			cards.append(f"{shape} {x}")
	blackjack_setCards(i.user.id, "player", [cards.pop(random.randint(0, len(cards)-1)), cards.pop(random.randint(0, len(cards)-1))])
	blackjack_setCards(i.user.id, "dealer", [cards.pop(random.randint(0, len(cards)-1)), cards.pop(random.randint(0, len(cards)-1))])
	blackjack_setCards(i.user.id, "remained", cards)
	embed = await blackjack_makeEmbed(i.user, betting, ch, True)
	if embed: await ch.send(embed=embed, view=blackjackView(i.user.id, doubleDown))
	await i.edit_original_message(f"스레드를 정상적으로 개설했어요.\n{ch.mention}으로 이동해주세요!")
	return