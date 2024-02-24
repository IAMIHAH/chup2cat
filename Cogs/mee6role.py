import disnake
from disnake.ext import commands
from disnake.utils import get
from mee6_py_api import API

class Mee6Role(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.slash_command(
        name=disnake.Localized(
            "mee6role",
            data={
                disnake.Locale.ko: "레벨역할"
            }
        ),
        description=disnake.Localized(
            "Get role from level which MEE6.",
            data={
                disnake.Locale.ko: "MEE6 레벨 역할을 획득합니다."
            }
        ),
        guild_ids=[812664224512868382]
    )
    async def level_role(i: disnake.CommandInteraction):
        await i.response.defer(ephemeral=True)
        details = await API(812664224512868382).levels.get_user_details(i.user.id)
        roles = []
        x = 0
        while True:
            x += 1
            if details['level'] >= x*10:
                role = get(i.guild.roles, name=f"{x*10}레벨")
                try:
                    await i.user.add_roles(role)
                    roles.append(role.mention)
                except:
                    break
            else:
                break
        if len(roles) > 0:
            await i.edit_original_message(content=f"현재 감지되는 MEE6 레벨: `{details['level']}`\n>>> {' '.join(roles)} 역할 지급이 완료되었습니다!")
        else:
            await i.edit_original_message(content=f"현재 감지되는 MEE6 레벨: `{details['level']}`\n>>> 얻을 역할이 없습니다.")

def setup(bot: commands.Bot):
    bot.add_cog(Mee6Role(bot))