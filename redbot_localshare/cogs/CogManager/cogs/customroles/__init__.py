from .customroles import CustomRoles


def setup(bot):
    bot.add_cog(CustomRoles(bot))
