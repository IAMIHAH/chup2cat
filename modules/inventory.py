import sqlite3, disnake
from .log import addLog

async def createInventory(user: disnake.Member):
	conn = sqlite3.connect("inventory.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"CREATE TABLE '{user.id}' (item TEXT PRIMARY KEY, amount INTEGER, data TEXT)")
	conn.close()

async def deleteInventory(user: disnake.Member):
	conn = sqlite3.connect("inventory.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"DROP TABLE '{user.id}'")
	conn.close()

async def getAllInventoryItems(user: int):
	conn = sqlite3.connect("inventory.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT * FROM '{user}'")
	n = c.fetchall()
	conn.close()
	return n

async def getInventoryItemAmount(user: int, item: str, data: str='{}'):
	conn = sqlite3.connect("inventory.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT amount FROM '{user}' WHERE item='{item}' AND data='{data}'")
	n = c.fetchone()
	conn.close()
	if n:
		return n[0]
	else:
		return 0

async def addInventoryItem(user: int, item: str, amount: int, cmdUserId: int=None, data: str='{}'):
	conn = sqlite3.connect("inventory.db", isolation_level=None)
	c = conn.cursor()
	try:
		c.execute(f"INSERT INTO '{user}'(item, amount, data) VALUES('{item}', {amount}, '{data}')")
	except sqlite3.IntegrityError:
		c.execute(f"UPDATE '{user}' SET amount=amount+{amount} WHERE item='{item}' AND data='{data}'")
	except sqlite3.OperationalError:
		c.execute(f"DROP TABLE '{user}';")
		c.execute(f'CREATE TABLE "{user}" (item TEXT, amount INTEGER, data TEXT, PRIMARY KEY("item", "data"))')
		c.execute(f"INSERT INTO '{user}'(item, amount, data) VALUES('{item}', {amount}, '{data}')")
	if cmdUserId:
		await addLog(event="AddItem", userId=user, cmdUserId=cmdUserId, item=item, itemAmount=amount)
	else:
		await addLog(event="GetItem", userId=user, item=item, itemAmount=amount)
	conn.close()

async def removeInventoryItem(user: int, item: str, amount: int, cmdUserId: int=None, data: str='{}'):
	conn = sqlite3.connect("inventory.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"UPDATE '{user}' SET amount=amount-{amount} WHERE item='{item}' AND data='{data}'")
	if cmdUserId:
		await addLog(event="RemoveItem", userId=user, cmdUserId=cmdUserId, item=item, itemAmount=amount)
	else:
		await addLog(event="UseItem", userId=user, gainedExp=0, item=item, itemAmount=amount)
	conn.close()