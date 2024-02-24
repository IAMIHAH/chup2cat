import disnake, asyncio, sqlite3
from disnake.ext import commands

class memberCount(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        if member.guild.id == 812664224512868382:
            await self.updateUserCount(member.guild)
            conn = sqlite3.connect('account.db')
            c = conn.cursor()
            c.execute(f"SELECT * FROM account WHERE discordId={member.id}")
            n = c.fetchone()
            if n:
                if n[2]:
                    await member.add_roles(member.guild.get_role(812668523464753192))
                    await member.add_roles(member.guild.get_role(1023898492797714452))
                    await member.remove_roles(member.guild.get_role(889825272927498251))
    
    @commands.Cog.listener()
    async def on_member_leave(self, member: disnake.Member):
        if member.guild.id == 812664224512868382:
            await self.updateUserCount(member.guild)

    async def updateUserCount(self, guild: disnake.Guild):
        ch = await guild.fetch_channel(1023562114872393798)
        await ch.edit(name=f"👤・{guild.member_count}명")
        await asyncio.sleep(2)
        ch = await guild.fetch_channel(1023563570660773918)
        await ch.edit(name=f"✅・{len(guild.get_role(812668523464753192).members)}명")
        await asyncio.sleep(2)
        ch = await guild.fetch_channel(1156552424358674472)
        await ch.edit(name=f"😺・{len(guild.get_role(1023898492797714452).members)}명")

def setup(bot: commands.Bot):
    bot.add_cog(memberCount(bot))