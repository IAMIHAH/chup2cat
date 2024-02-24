import sqlite3, time

async def fetchLog(userId: int, time: float, event: str):
    """### fetchLog

    Args:
        userId `int`
            Discord user id.
                ex) 741973166364164099
        time `float`
            Timestamp.
                ex) 1674482277.6166852
        event `str`
            Event name.
                ex) `ExpFromChat` `ExpFromAdmin` `UseItem` `GetItem` `AddItem` `RemoveItem`

    Returns:
        `tuple`
            Fetched a log.
    """
    conn = sqlite3.connect("log.db", isolation_level=None)
    c = conn.cursor()
    c.execute(f"SELECT * FROM log WHERE userId={userId} AND event='{event}' AND time={time}")
    n = c.fetchone()
    conn.close()
    return n

async def fetchLogs(userId: int, page: int=1):
    """### fetchLogs

    Args:
        userId `int`
            Discord user id.
                ex) 741973166364164099

    Returns:
        `list[tuple]`
            Fetched logs.
    """
    conn = sqlite3.connect("log.db", isolation_level=None)
    c = conn.cursor()
    c.execute(f"SELECT time,event,gainedExp FROM log WHERE userId={userId} ORDER BY time DESC LIMIT {(page-1)*25-1},25")
    n = c.fetchall()
    conn.close()
    return n

async def fetchLogsWithEvent(userId: int, event: str, page: int=1):
    """### fetchLogsWithEvent

    Args:
        userId `int`
            Discord user id.
                ex) 741973166364164099
        event `str`
            Event name.
                ex) `ExpFromChat` `ExpFromAdmin` `UseItem` `GetItem` `AddItem` `RemoveItem`

    Returns:
        `list[tuple]`
            Fetched logs.
    """
    conn = sqlite3.connect("log.db", isolation_level=None)
    c = conn.cursor()
    c.execute(f"SELECT time,event,gainedExp FROM log WHERE userId={userId} AND event='{event}' ORDER BY time DESC LIMIT {(page-1)*25-1},25")
    n = c.fetchall()
    conn.close()
    return n

async def addLog(event: str, userId: int, gainedExp: float = None, cmdUserId: int = None, item: str = None, itemAmount: int = None, chId: int = None, msgId: int = None):
    """### addLog

    Args:
        event `str`
            Event name.
                ex) `ExpFromChat` `ExpFromAdmin` `UseItem` `GetItem` `AddItem` `RemoveItem`
        userId `int`
            Discord user id.
                ex) 741973166364164099

        gainedExp `float`
            Gained EXP.
                ex) 17.43
        cmdUserId `int`
            User using command. `ExpFromAdmin` `AddItem` `RemoveItem`
                ex) 741973166364164099
        item `str`
            Item id. `UseItem` `GetItem` `AddItem` `RemoveItem`
                ex) `test-item`
        itemAmount `int`
            Item amount. `UseItem` `GetItem` `AddItem` `RemoveItem`
                ex) 1
        chId `int`
            Discord channel id. `ExpFromChat`
                ex) 812664224512868387
        msgId `int`
            Discord message id. `ExpFromChat`
                ex) 812664241521033266
    """
    conn = sqlite3.connect("log.db", isolation_level=None)
    c = conn.cursor()
    logTime = time.time()
    if event == "ExpFromChat":
        c.execute(f"INSERT INTO log(time, event, userId, gainedExp, chId, msgId) VALUES({logTime}, 'ExpFromChat', {userId}, {gainedExp}, {chId}, {msgId})")
    if event == "ExpFromAdmin":
        c.execute(f"INSERT INTO log(time, event, userId, gainedExp, cmdUserId) VALUES({logTime}, 'ExpFromAdmin', {userId}, {gainedExp}, {cmdUserId})")
    if event == "UseItem":
        c.execute(f"INSERT INTO log(time, event, userId, gainedExp, item, itemAmount) VALUES({logTime}, 'UseItem', {userId}, {gainedExp}, '{item}', {itemAmount})")
    if event == "GetItem":
        c.execute(f"INSERT INTO log(time, event, userId, item, itemAmount) VALUES({logTime}, 'GetItem', {userId}, '{item}', {itemAmount})")
    if event == "AddItem":
        c.execute(f"INSERT INTO log(time, event, userId, cmdUserId, item, itemAmount) VALUES({logTime}, 'AddItem', {userId}, {cmdUserId}, '{item}', {itemAmount})")
    if event == "RemoveItem":
        c.execute(f"INSERT INTO log(time, event, userId, cmdUserId, item, itemAmount) VALUES({logTime}, 'RemoveItem', {userId}, {cmdUserId}, '{item}', {itemAmount})")
    if event == "SeasonEnd":
        c.execute(f"INSERT INTO log(time, event, userId) VALUES({logTime}, 'SeasonEnd', {userId})")
    if event == "Attendance" or event == "AttendanceMore7" or event == "AttendanceMore31":
        c.execute(f"INSERT INTO log(time, event, userId, gainedExp) VALUES({logTime}, '{event}', {userId}, {gainedExp})")
    conn.close()