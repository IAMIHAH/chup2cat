import ast

def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

import disnake, sqlite3
from disnake.ext import commands

class evalCmd(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
	
	@commands.command(name="eval")
	async def eval_fn(self, ctx, *, cmd):
		fn_name = "_eval_expr"

		cmd = cmd.strip("` ")

		# add a layer of indentation
		cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

		# wrap in async def body
		body = f"async def {fn_name}():\n{cmd}"

		parsed = ast.parse(body)
		body = parsed.body[0].body

		insert_returns(body)

		env = {
			'bot': ctx.bot,
			'disnake': disnake,
			'commands': commands,
			'ctx': ctx,
			'__import__': __import__
		}
		exec(compile(parsed, filename="<ast>", mode="exec"), env)

		result = (await eval(f"{fn_name}()", env))
		await ctx.send(result)

def setup(bot: commands.Bot):
	bot.add_cog(evalCmd(bot))