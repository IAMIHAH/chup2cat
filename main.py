import disnake, os
from disnake.ext import commands
from config import BOT_TOKEN, SERVER, VERSION

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=disnake.Intents.all())

for filename in os.listdir("Cogs"):
	if filename.endswith(".py"):
		bot.load_extension(f"Cogs.{filename[:-3]}")

@bot.event
async def on_ready():
	print(f"Ready! {bot.user.name}#{bot.user.discriminator}")
	await bot.change_presence(activity=disnake.Game(name=f"{VERSION}"))

@bot.event
async def on_thread_create(thread: disnake.Thread):
	if thread.guild.id == 812664224512868382:
		await thread.join()

@bot.slash_command(
	name="reload",
	description="Reload Module (Cogs)",
	guild_ids=[812664224512868382]
)
async def reloadCogs(
	i: disnake.CommandInteraction,
	file: str = commands.Param(
		name="module",
		description="Module name."
	)
):
	try:
		bot.reload_extension(name=f"Cogs.{file}")
		await i.response.send_message(":white_check_mark: Reload completed.")
	except Exception as e:
		print(e)
		await i.response.send_message(":x: Reload failed.")

@bot.slash_command(
	name="load",
	description="Reload Module (Cogs)",
	guild_ids=[812664224512868382]
)
async def loadCogs(
	i: disnake.CommandInteraction,
	file: str = commands.Param(
		name="module",
		description="Module name."
	)
):
	try:
		bot.load_extension(name=f"Cogs.{file}")
		await i.response.send_message(":white_check_mark: Load completed.")
	except Exception as e:
		print(e)
		await i.response.send_message(":x: Load failed.")

@bot.slash_command(
	name="unload",
	description="Unload Module (Cogs)",
	guild_ids=[812664224512868382]
)
async def unloadCogs(
	i: disnake.CommandInteraction,
	file: str = commands.Param(
		name="module",
		description="Module name."
	)
):
	try:
		bot.load_extension(name=f"Cogs.{file}")
		await i.response.send_message(":white_check_mark: Unload completed.")
	except Exception as e:
		print(e)
		await i.response.send_message(":x: Unload failed.")

bot.run(BOT_TOKEN[SERVER])