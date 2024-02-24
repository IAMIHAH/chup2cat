import disnake, sqlite3
from config import SEASON
	
async def expReset(user: disnake.Member, new: bool=False):
	conn = sqlite3.connect("user.db", isolation_level=None)
	c = conn.cursor()
	if new:
		c.execute(f"INSERT INTO '{SEASON}'(userId, exp, level, cooldown) VALUES({user.id}, 0, 0, 0)")
	else: c.execute(f"UPDATE '{SEASON}' SET exp=0,level=1 WHERE userId={user.id}")
	conn.close()

async def expNow(user: disnake.Member, season: str=SEASON):
	conn = sqlite3.connect("user.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT exp,level FROM '{season}' WHERE userId={user.id}")
	n = c.fetchone()
	conn.close()
	if n:
		return [round(float(n[0]), 3), int(n[1])]
	else:
		await expReset(user=user, new=True)
		return [float(0), int(0)]

def expNextLevelExp(nowLevel: int):
	a = round(( 5 / 6 * nowLevel * (2 * nowLevel * nowLevel + 27 * nowLevel + 91) ) * 1.6, 3)
	if a.is_integer(): return int(a)
	else: return a

async def expAdd(user: disnake.Member, exp: float, cooldown: float=None):
	conn = sqlite3.connect("user.db", isolation_level=None)
	c = conn.cursor()
	nowExp = await expNow(user=user)
	c.execute(f"UPDATE '{SEASON}' SET exp={nowExp[0]+exp} WHERE userId={user.id}")
	if cooldown: c.execute(f"UPDATE '{SEASON}' SET cooldown={cooldown} WHERE userId={user.id}")
	conn.close()

async def expAdd_ID(user: id, exp: float, cooldown: float=None):
	conn = sqlite3.connect("user.db", isolation_level=None)
	c = conn.cursor()
	#nowExp = await expNow(user=user)
	c.execute(f"UPDATE '{SEASON}' SET exp=exp+{exp} WHERE userId={user}")
	if cooldown: c.execute(f"UPDATE '{SEASON}' SET cooldown={cooldown} WHERE userId={user}")
	conn.close()

async def expRemoved(user: disnake.Member, exp: float):
	conn = sqlite3.connect("user.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"UPDATE '{SEASON}' SET exp=exp-{exp} WHERE userId={user.id}")
	conn.close()

async def expLevelUp(user: disnake.Member):
	now = await expNow(user)
	nowLevel = now[1]+1
	nextLevelExp = expNextLevelExp(nowLevel)
	while True:
		if now[0] > nextLevelExp:
			nowLevel += 1
			nextLevelExp = expNextLevelExp(nowLevel)
		else:
			break
	await expLevelSet(user=user, level=nowLevel-1)
	if nowLevel-1 > now[1]:
		return nowLevel-1

async def expLevelDown(user: disnake.Member):
	now = await expNow(user)
	nowLevel = now[1]
	nextLevelExp = expNextLevelExp(nowLevel)
	while True:
		if now[0] < nextLevelExp:
			nowLevel -= 1
			nextLevelExp = expNextLevelExp(nowLevel)
		else:
			break
	await expLevelSet(user=user, level=nowLevel)
	if nowLevel-1 < now[1]:
		return nowLevel-1

async def expLevelSet(user: disnake.Member, level: int):
	conn = sqlite3.connect("user.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"UPDATE '{SEASON}' SET level={level} WHERE userId={user.id}")
	conn.close()

async def expCooldown(user: disnake.Member):
	conn = sqlite3.connect("user.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT cooldown FROM '{SEASON}' WHERE userId={user.id}")
	n = c.fetchone()
	conn.close()
	if n:
		return n[0]
	else:
		return 0