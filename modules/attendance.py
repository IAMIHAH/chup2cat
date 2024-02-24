import disnake, sqlite3, datetime, calendar

def getAttendanceSeason():
	now = datetime.datetime.now()
	return f"attendance-{now.year}-{now.month if now.month >= 10 else f'0{now.month}'}"

def createAttendanceTable():
	now = datetime.datetime.now()
	last_day = calendar.monthrange(now.year, now.month)[1]
	columns = []
	for x in range(1, last_day+1): columns.append(f"'day{x}' INTEGER DEFAULT 0")

	conn = sqlite3.connect("attendance.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"CREATE TABLE '{getAttendanceSeason()}'('userId' INTEGER PRIMARY KEY, {', '. join(columns)})")
	conn.close()

async def attendanceUp(user: disnake.Member, day: int=None):
	if not day: day = datetime.datetime.now().day
	conn = sqlite3.connect("attendance.db", isolation_level=None)
	c = conn.cursor()
	await getAttendance(user, day)
	c.execute(f"UPDATE '{getAttendanceSeason()}' SET day{day}=day{day}+1 WHERE userId={user.id}")
	conn.close()

async def getAttendance(user: disnake.Member, day: int=None) -> int:
	if not day: day = datetime.datetime.now().day
	conn = sqlite3.connect("attendance.db", isolation_level=None)
	c = conn.cursor()
	c.execute(f"SELECT day{day} FROM '{getAttendanceSeason()}' WHERE userId={user.id}")
	n = c.fetchone()
	if n:
		conn.close()
		return n[0]
	else:
		try:
			c.execute(f"INSERT INTO '{getAttendanceSeason()}'(userId) VALUES({user.id})")
		except sqlite3.OperationalError as e:
			if "no such table" in f"{e}": createAttendanceTable()
			else: print(e.with_traceback())
		except sqlite3.IntegrityError as e:
			if "UNIQUE" in f"{e}": pass
			else: print(e.with_traceback())
		conn.close()
		return 0

async def getAttendanceCalendar(user: disnake.Member):
	now = datetime.datetime.now()
	cal = calendar.monthcalendar(now.year, now.month)
	maxday = calendar.monthrange(now.year, now.month)[1]

	# Mon ~ Sun → Sun ~ Sat
	for x in range(len(cal)):
		for j in range(7):
			if cal[len(cal)-1-x][6-j] != 0:
				if 6-j == 6 and len(cal)-1-x == len(cal)-1: cal.append([cal[len(cal)-1][6]+1,0,0,0,0,0,0])
				else: cal[len(cal)-1-x][6-j] = cal[len(cal)-1-x][6-j]-1
			if cal[len(cal)-1-x][5-j] == maxday: cal[len(cal)-1-x][6-j] = maxday
	if cal[0] == [0,0,0,0,0,0,0]: cal.pop(0)
	
	conn = sqlite3.connect("attendance.db", isolation_level=None)
	c = conn.cursor()
	
	# Rendering
	result = []
	for x in range(len(cal)):
		rs = []
		for j in range(7):
			if cal[x][j] > 0:
				c.execute(f"SELECT day{cal[x][j]} FROM '{getAttendanceSeason()}' WHERE userId={user.id}")
				n = c.fetchone()
				if n[0] >= 2: cal[x][j] = f"{cal[x][j]}√" if cal[x][j] >= 10 else f"{cal[x][j]}√ "
				elif n[0] == 1: cal[x][j] = f"{cal[x][j]}·" if cal[x][j] >= 10 else f"{cal[x][j]}· "
				else: cal[x][j] = f"{cal[x][j]} " if cal[x][j] >= 10 else f"{cal[x][j]}  "
			else:
				cal[x][j] = "   "
			rs.append(cal[x][j])
		result.append(' '.join(rs))
	res = '\n'.join(result)
	return f"```arm\nSun Mon Tue Wed Thu Fri Sat\n───────────────────────────\n{res}\n```"

async def getAttendanceMore(user: disnake.Member, days: int = 7):
	now = datetime.datetime.now()
	cal = calendar.monthcalendar(now.year, now.month)
	maxday = calendar.monthrange(now.year, now.month)[1]

	# Mon ~ Sun → Sun ~ Sat
	for x in range(len(cal)):
		for j in range(7):
			if cal[len(cal)-1-x][6-j] != 0:
				if 6-j == 6 and len(cal)-1-x == len(cal)-1: cal.append([cal[len(cal)-1][6]+1,0,0,0,0,0,0])
				else: cal[len(cal)-1-x][6-j] = cal[len(cal)-1-x][6-j]-1
			if cal[len(cal)-1-x][5-j] == maxday: cal[len(cal)-1-x][6-j] = maxday
	if cal[0] == [0,0,0,0,0,0,0]: cal.pop(0)
	
	conn = sqlite3.connect("attendance.db", isolation_level=None)
	c = conn.cursor()
	
	result = []
	# attendance condition check
	if days == 7:
		for x in range(len(cal)):
			if now.day in cal[x]:
				for j in range(7):
					if cal[x][j] > 0:
						c.execute(f"SELECT day{cal[x][j]} FROM '{getAttendanceSeason()}' WHERE userId={user.id}")
						n = c.fetchone()
						if n[0] >= 2: result += 1
		if result >= 7: return True
		else: return False
	elif days == 31:
		for x in range(len(cal)):
			for j in range(7):
				if cal[x][j] > 0:
					c.execute(f"SELECT day{cal[x][j]} FROM '{getAttendanceSeason()}' WHERE userId={user.id}")
					n = c.fetchone()
					if n[0] >= 2: result += 1
		last_day = calendar.monthrange(now.year, now.month)[1]
		if result >= last_day: return True
		else: return False