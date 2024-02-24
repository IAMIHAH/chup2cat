import sqlite3

async def churAdd(user: int):
	conn = sqlite3.connect("chur.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT * FROM chur WHERE userId={user}")
	n = c.fetchone()
	if not n:
		c.execute(f"INSERT INTO chur VALUES({user}, 0, 0)")
	c.execute(f"UPDATE chur SET chur=chur+3 WHERE userId={user}")
	conn.close()

nowEvent = "halloween"
point = "point"

async def eventPointAdd(user: int, addPoints: int=1, point: str=point):
	conn = sqlite3.connect(f"{nowEvent}.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT * FROM {nowEvent} WHERE userId={user}")
	n = c.fetchone()
	if not n:
		c.execute(f"INSERT INTO {nowEvent}(userId) VALUES({user})")
	c.execute(f"UPDATE {nowEvent} SET {point}={point}+{addPoints} WHERE userId={user}")
	conn.close()

async def getEventPoint(user: int, point: str=point):
	conn = sqlite3.connect(f"{nowEvent}.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT {point} FROM {nowEvent} WHERE userId={user}")
	n = c.fetchone()
	conn.close()
	if n and n[0]: return n[0]
	else: return 0