import sqlite3, disnake

async def getItemName(item: str, locale: disnake.Locale):
	conn = sqlite3.connect("item.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT {'ko' if locale == disnake.Locale.ko else 'en'} FROM Items WHERE itemId='{item}'")
	n = c.fetchone()
	conn.close()
	return n[0]

async def getItemEmoji(item: str):
	conn = sqlite3.connect("item.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT emoji FROM Items WHERE itemId='{item}'")
	n = c.fetchone()
	conn.close()
	return n[0]

async def getItemFull(item: str, locale: disnake.Locale):
	conn = sqlite3.connect("item.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT emoji,{'ko' if locale == disnake.Locale.ko else 'en'} FROM Items WHERE itemId='{item}'")
	n = c.fetchone()
	conn.close()
	return f'{n[0]} {n[1]}'

async def getItemDesc(item: str, locale: disnake.Locale):
	conn = sqlite3.connect("item.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT desc_{'ko' if locale == disnake.Locale.ko else 'en'} FROM Items WHERE itemId='{item}'")
	n = c.fetchone()
	conn.close()
	return n[0]