from discord import Bot, Intents, ApplicationContext, Member, Embed
from orm import Transaction, LedgerEntry
from tortoise import Tortoise, connections
from os import getenv
from pytz import timezone
from dotenv import load_dotenv
load_dotenv()

bot = Bot(
    help_command=None,
    intents=Intents.all(),
    auto_sync_commands=True,
    debug_guilds=[1362433756710961302]
)

tz = timezone('Asia/Taipei')

userList = [551024169442344970, 605999614000365588, 499528798824300544]

@bot.event
async def on_connect():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['orm']}
    )
    await Tortoise.generate_schemas()
    print("Database connected and schemas generated.")

@bot.event
async def on_disconnect():
    await connections.close_all()
    print("Database connections closed.")

@bot.event
async def on_ready():
    if not bot.user:
        return
    await bot.sync_commands()
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

async def update_balance():
    pass

@bot.slash_command(name='split', name_localizations={'zh-TW': '平分'})
async def split(ctx: ApplicationContext, amount: int, description: str = "無描述"):
    amount_div = amount // 3
    await ctx.respond(f'平分後每人應付 {amount_div} 元，事由：{description}')
    trans = Transaction(description = description, recorded_by_id = ctx.author.id)
    await trans.save()
    for user_id in userList:
        user_amount = amount_div if user_id != ctx.author.id else -2 * amount_div
        await LedgerEntry(user_id=user_id, amount=user_amount, transaction=trans).save()
    await update_balance()

@bot.slash_command(name='receive', name_localizations={'zh-TW': '收款'})
async def receive(ctx: ApplicationContext, member: Member, amount: int, description: str = "無描述"):
    trans = Transaction(description=description, recorded_by_id=ctx.author.id)
    await trans.save()
    await LedgerEntry(user_id=member.id, amount=amount, transaction=trans).save()
    await LedgerEntry(user_id=ctx.author.id, amount=-amount, transaction=trans).save()
    await ctx.respond(f'已向 {member.mention} 收款 {amount} 元，事由：{description}')

@bot.slash_command(name='pay', name_localizations={'zh-TW': '付款'})
async def pay(ctx: ApplicationContext, member: Member, amount: int, description: str = "無描述"):
    trans = Transaction(description=description, recorded_by_id=ctx.author.id)
    await trans.save()
    await LedgerEntry(user_id=member.id, amount=-amount, transaction=trans).save()
    await LedgerEntry(user_id=ctx.author.id, amount=amount, transaction=trans).save()
    await ctx.respond(f'已向 {member.mention} 付款 {amount} 元，事由：{description}')

@bot.slash_command(name='record', name_localizations={'zh-TW': '記錄'})
async def record(ctx: ApplicationContext):
    entries = await LedgerEntry.filter(user_id=ctx.author.id).order_by("transaction_id").limit(10).prefetch_related('transaction')
    embed = Embed(title="最近的交易記錄", color=0x00ff00)
    for entry in entries:
        time = entry.transaction.created_at.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
        embed.add_field(name=entry.transaction.description, value=f"{['付', '收'][entry.amount < 0]} {abs(entry.amount)} 元\n時間: {time}", inline=False)
    await ctx.respond(embed=embed, ephemeral=True)

try:
    bot.loop.run_until_complete(bot.start(getenv("DISCORD_TOKEN", "")))
except KeyboardInterrupt:
    pass
finally:
    bot.loop.run_until_complete(bot.close())
    bot.loop.close()
