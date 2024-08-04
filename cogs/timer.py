import discord
import asyncio
from scripts.support import get_json
from discord.ext import commands

phrases = get_json("./phrases.json")


class TimerCog(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.slash_command(description="Ставит таймер, можно определить сообщение, "
                                       "которое будет показываться по окончанию таймера")
    async def set_timer(self, ctx, time_input, end_message: str = "Таймер истек!"):
        try:
            try:
                time = int(time_input)
            except ValueError:
                convert_time_list = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'S': 1, 'M': 60, 'H': 3600, 'D': 86400}
                time = int(time_input[:-1]) * convert_time_list[time_input[-1]]
            if time > 86400:
                await ctx.respond("Я не могу считать дольше чем 24 часа, пожалей меня, "
                                  "попробуй так же 100 тысяч секунд считать, посмотрим на тебя после этого")
                return
            if time <= 0:
                await ctx.respond("Время не может быть отрицательным. Тебя этому в школе не учили что ли?")
                return
            if time >= 3600:
                message = await ctx.respond(
                    f"Таймер {ctx.author}: {time // 3600} часов {time % 3600 // 60} минут {time % 60} секунд")
            elif time >= 60:
                message = await ctx.respond(f"Таймер {ctx.author}: {time // 60} минут {time % 60} секунд")
            else:
                message = await ctx.respond(f"Таймер {ctx.author}: {time} секунд")
            while True:
                try:
                    await asyncio.sleep(5)
                    time -= 5
                    if time >= 3600:
                        await message.edit(
                            content=f"Таймер {ctx.author}: {time // 3600} часов {time % 3600 // 60} минут {time % 60} секунд")
                    elif time >= 60:
                        await message.edit(content=f"Таймер {ctx.author}: {time // 60} минут {time % 60} секунд")
                    elif time < 60:
                        await message.edit(content=f"Таймер {ctx.author}: {time} секунд")
                    if time <= 0:
                        await message.edit(content=f"{ctx.author.mention} {end_message}")
                        break
                except Exception:
                    break
        except ValueError:
            await ctx.respond(f"Че это вообще такое **{time_input}**, формулируй нормально, я ничего не понял")


def setup(bot):
    bot.add_cog(TimerCog(bot))
