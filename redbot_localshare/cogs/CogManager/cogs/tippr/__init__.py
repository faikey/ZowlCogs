from .tippr import Tippr


def setup(bot):
    bot.add_cog(Tippr(bot.loop))
