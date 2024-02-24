import disnake, sqlite3
from modules.exp import expNow
from modules.item import getItemEmoji, getItemName
from config import SEASON

async def seasonPassReward(level: int, itemNumber: int):
	conn = sqlite3.connect("season.db", isolation_level=None)
	c = conn.cursor()
	if itemNumber >= 4:
		c.execute(f"SELECT premium,premium_amount,premium_data FROM '{SEASON}' WHERE level={level}")
	else:
		c.execute(f"SELECT item{itemNumber},item{itemNumber}_amount,item{itemNumber}_data FROM '{SEASON}' WHERE level={level}")
	n = c.fetchone()
	conn.close()
	return n

async def getUserRewarded(userId: int, level: int, rewardId: int):
	conn = sqlite3.connect("reward.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT rewarded FROM '{SEASON}' WHERE userId={userId} AND level={level} AND rewardId={rewardId}")
	n = c.fetchone()
	conn.close()
	if n and n[0] == 1:
		return True
	else:
		return False

async def addUserRewarded(userId: int, level: int, rewardId: int, rewarded: int=1):
	conn = sqlite3.connect("reward.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"INSERT INTO '{SEASON}'(userId, level, rewardId, rewarded) VALUES({userId}, {level}, {rewardId}, {rewarded})")
	conn.close()

async def getUserPremium(user: disnake.Member):
	if user.get_role(853457470655823882): # 1096745880104730664
		return True
	return False

async def seasonPassRewardOptions(user: disnake.Member, locale: disnake.Locale, premium=False, page=1):
	options = []
	length = 0
	for level in range(0, (await expNow(user))[1]+2):
		for x in range(1, 5):
			a = await seasonPassReward(level=level, itemNumber=x)
			if a and a[0]:
				optionAppend = True
				if (await expNow(user))[1] < level:
					emoji = "❌"
				elif (await getUserRewarded(user.id, level, x)):
					optionAppend = False
				else:
					emoji = "🎁"
				if x == 4 and not premium:
					emoji = "❌"
				if optionAppend:
					length += 1
					if (page-1)*25 < length <= page*25:
						options.append(
							disnake.SelectOption(
								label=f"레벨 {level} 보상 #{x if x < 4 else 'Premium'} {emoji}",
								description=f"{await getItemName(item=a[0], locale=locale)}×{a[1]}",
								value=f"{level}/{x}",
								emoji=(await getItemEmoji(item=a[0]))
							)
						)
	return [options, True if length > 25 and len(options) == 25 else False]