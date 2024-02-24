import disnake
from disnake.ext import commands
from modules.embed import makeErrorEmbed
from modules.item import getItemFull
from modules.inventory import addInventoryItem, getInventoryItemAmount, removeInventoryItem

class management(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
	
	async def gamble_checkMoney(self, user: disnake.Member, betting: int):
		meowCoin = await getInventoryItemAmount(user=user.id, item="meow-coin")
		if meowCoin >= betting:
			return True
		return False

	@commands.slash_command(
		name=disnake.Localized(
			"manage",
			data={
				disnake.Locale.ko: "관리"
			}
		),
		guild_ids=[812664224512868382,742188157424107679]
	)
	async def manage_slashCommands(self, i: disnake.CommandInteraction):
		return

	@manage_slashCommands.sub_command(
		name="인벤토리추가",
		description="유저 인벤토리에 아이템 추가",
		options=[
			disnake.Option(
				name="유저",
				description="유저",
				type=disnake.OptionType.user,
				required=True
			),
			disnake.Option(
				name="아이템",
				description="아이템 아이디",
				type=disnake.OptionType.string,
				required=True
			),
			disnake.Option(
				name="수량",
				description="수량",
				type=disnake.OptionType.integer,
				required=True
			),
			disnake.Option(
				name="옵션",
				description="아이템 옵션 JSON (*입력 주의)",
				type=disnake.OptionType.string
			)
		],
		connectors={
			"유저": "user",
			"아이템": "item",
			"수량": "amount",
			"옵션": "options"
		}
	)
	async def inventoryAdd_sc(
		self,
		i: disnake.CommandInteraction,
		user: disnake.Member,
		item: str,
		amount: int,
		options: str='{}'
	):
		last = await getInventoryItemAmount(user.id, item, options)
		await addInventoryItem(user.id, item, amount, i.user.id, options)
		now  = await getInventoryItemAmount(user.id, item, options)
		embed = disnake.Embed(
			title="✅ 추가 완료!"
		)
		embed.add_field(name="아이템", value=f"{await getItemFull(item, i.locale)}\n`{options}`", inline=False)
		embed.add_field(name="획득 전 수량", value=f"`{last}`")
		embed.add_field(name="획득 수량", value=f"→ `{f'+{amount}' if amount >= 0 else amount}` →")
		embed.add_field(name="획득 후 수량", value=f"`{now}`")
		await i.response.send_message(embed=embed, ephemeral=True)

def setup(bot: commands.Bot):
	bot.add_cog(management(bot))