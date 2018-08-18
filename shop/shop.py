# Standard Library
import asyncio
import csv
import logging
import os
import random
import textwrap
import uuid
from bisect import bisect
from copy import deepcopy
from itertools import zip_longest
import json


# Shop
from .menu import ShopMenu
from .inventory import Inventory
from .checks import Checks

# Discord.py
import discord
from discord.ext import commands

# Red
from redbot.core import Config, bank, commands
from redbot.core.data_manager import cog_data_path, bundled_data_path

log = logging.getLogger("red.shop")

__version__ = "3.0.07"
__author__ = "Redjumpman"


def global_permissions():
    """
     Returns true if shop is global, otherwise checks if the
     command was used by guild owner or guild administrator
    """
    async def pred(ctx: commands.Context):
        author = ctx.author
        if await ctx.bot.is_owner(author):
            return True
        if not await Shop().shop_is_global():
            permissions = ctx.channel.permissions_for(author)
            return author == ctx.guild.owner or permissions.administrator

    return commands.check(pred)


def guild_required_or_global():
    async def pred(ctx: commands.Context):
        if await Shop().shop_is_global():
            return True
        elif not await Shop().shop_is_global() and ctx.guild is not None:
            return True
        else:
            return False
    return commands.check(pred)


class Shop:
    shop_defaults = {
        'Shops': {},
        'Settings': {
            'Alerts': False,
            'Alert_Role': 'Admin',
            'Closed': False,
        },
        'Pending': {}
    }
    member_defaults = {
        'Inventory': {},
        'Trading': True,
    }
    user_defaults = member_defaults
    global_defaults = shop_defaults
    global_defaults['Global'] = False

    def __init__(self):
        self.db = Config.get_conf(self, 5074395003, force_registration=True)
        self.db.register_guild(**self.shop_defaults)
        self.db.register_global(**self.global_defaults)
        self.db.register_member(**self.member_defaults)
        self.db.register_user(**self.user_defaults)

    # -----------------------COMMANDS-------------------------------------

    # unit tests
    # @commands.command()
    # async def testA(self, ctx, user=None):

    #     # should output the following
    #     # 1
    #     # 6
    #     #4

    #     inventory = await self.get_instance(ctx, user=ctx.author)


    #     # a = await self.update_attr(ctx, ctx.author, "Fire Sword", {'test': 50})
    #     # print(a)

    #     # b = await self. get_attr(ctx, ctx.author, "Fire Sword", ['test'])
    #     # print(b)

    #     async def attr_tests( danger_mode=False):
    #         tests = []

    #         print('[attr_test] SET & GET test...')
    #         await self.set_attr(ctx, user, 'Fire Sword', {'test1': 1}, danger_mode=danger_mode)
    #         test = await self.get_attr(ctx, user, 'Fire Sword', ['test1'], danger_mode=danger_mode)
    #         tests.append(test)
    #         if test != {'test1': 1}:
    #             print('[attr_test] SET & GET test failed')

    #         print('[attr_test] UPDATE & GET inc test...')
    #         await self.update_attr(ctx, user, 'Fire Sword', {'test1': 5}, danger_mode=danger_mode)
    #         test = await self.get_attr(ctx, user, 'Fire Sword', ['test1'], danger_mode=danger_mode)
    #         tests.append(test)
    #         if test != {'test1': 6}:
    #             print('[attr_test] UPDATE & GET inc test failed')


    #         print('[attr_test] UPDATE & GET dec test...')
    #         await self.update_attr(ctx, user, 'Fire Sword', {'test1': -2}, danger_mode=danger_mode)
    #         test = await self.get_attr(ctx, user, 'Fire Sword', ['test1'], danger_mode=danger_mode)
    #         tests.append(test)
    #         if test != {'test1': 4}:
    #             print('[attr_test] UPDATE & GET dec test failed')


    #         print('[attr_test] UPDATE no default test...')
    #         try: 
    #             await self.update_attr(ctx, user, 'Fire Sword', {'DoesntExist': 5}, danger_mode=danger_mode)
    #         except KeyError:
    #             pass
    #         else:
    #             print('[attr_test] UPDATE no default test failed')


    #         print('[attr_test] UPDATE & GET default test...')
    #         await self.update_attr(ctx, user, 'Fire Sword', {'DoesntExist': 5}, {'DoesntExist': 0}, danger_mode=danger_mode)
    #         test = await self.get_attr(ctx, user, 'Fire Sword', ['DoesntExist'], danger_mode=danger_mode)
    #         tests.append(test)
    #         if test != {'DoesntExist': 5}:
    #             print('[attr_test] UPDATE & GET default test failed')

    #         print(tests)

        
    #     await attr_tests(False)





    """
    Adds attributes to an item belonging to a user
    
    Parameters
    ----------
        ctx : discord.Message 
            context to get the guild to fetch inventory from
        user : (discord.member)
            member object representing a users discord account
        item_name : str
            name of the item to add the attributes to
        attributes : dict
            dict containing the attributes to add 
            e.g. {charges: 3, damage: 15} 
        danger_mode : bool
            enables direct editing of the item in a users inventory. This allows you to do things like editing the quantity of an item that a user has. 
            ***Using this setting is dangerous can can brick the users inventory, using it is not recommended.

            default values you can (but shouldn't) edit:
                Cost
                Qty
                Type
                Info
                Role
                Messages

    Raises
    ------
        KeyError
            if the user doesnt have the item specified

    """
    async def set_attr(self, ctx, user: discord.Member, item_name, attributes: dict, danger_mode=False):
        if user is None:
            user = ctx.author

        usr_inventory = await self._get_check_inv(ctx, user, item_name)


        for key, value in attributes.items():
            await usr_inventory.set_raw('Inventory', item_name, *self._check_danger(danger_mode), key, value=value)



    """
    Gets attributes from a user's item

    if you want to get all of an item's attibutes look into the 'inv_hook' method

    Parameters
    ----------
        ctx : discord.Message 
            context to get the guild to fetch inventory from
        user : discord.Member
            member object representing a users discord account
        item_name : str
            name of the item to get the attributes from
        attributes : list
            list containing the attributes to fetch 
            e.g. ['charges', 'damage'] 
        danger_mode : bool
            gets a value that was set using danger mode
            ***Using this setting is dangerous can can brick the users inventory, using it is not recommended
        
    Returns
    -------
        dict
            dict containing the attributes you passed in with their respective values
            if an attribute doesn't exist it will return None

    Raises
    ------
        KeyError
            if the user doesn't have the item specified

    """
    async def get_attr(self, ctx, user: discord.Member, item_name, attributes: list, danger_mode=False):
        if user is None:
            user = ctx.author

        usr_inventory = await self._get_check_inv(ctx, user, item_name)
        returns = {}


        for key in attributes:
            try:
                returns[key] = await usr_inventory.get_raw('Inventory', item_name, *self._check_danger(danger_mode), key)
            except KeyError as a:
                returns[key] = None

        return returns


    """
    Increments or decrements attributes from a user's item and returns the new values

    If an attribute doesn't exist (or its value is None), it will check for the default value from the optional 'default_values' parameter. 
    If a default isn't specified *and the attribute doesn't exist* an error will be thrown. You can also choose to not set the default values and catch possible errors yourself

    Parameters
    ----------
        ctx : discord.Message 
            context to get the guild to fetch inventory from
        user : discord.Member
            member object representing a users discord account
        item_name : str
            name of the item to get the attributes from
        attributes : dict
            dict containing the attribute and how much to increment or decrement
            e.g. {charges: -1, damage: 2.5}
                this would decrement the 'charges' attribute by 1 and increment 'damage' by 2.5
        default_values : dict
            dict containing the default values if an attribute isn't set
        danger_mode : bool
           enables direct editing of the item in a users inventory. This allows you to do things like editing the quantity of an item that a user has. 
           ***Using this setting is dangerous can can brick the users inventory, using it is not recommended.

           default values you can (but shouldn't) edit:
               Cost
               Qty
               Type
               Info
               Role
               Messages
        
    Returns
    -------
        dict
            dict containing the new values of the attributes you passed in

    Raises
    ------
        KeyError
            if the user doesn't have the item specified
        TypeError
            if one of the attributes is non-number

    """
    async def update_attr(self, ctx, user: discord.Member, item_name, attributes: dict, default_values: dict=None, danger_mode=False):
        if user is None:
            user = ctx.author

        usr_inventory = await self._get_check_inv(ctx, user, item_name)


        attr_list = []
        for key, value in attributes.items():
            attr_list.append(key)

        attrs = await self.get_attr(ctx, user, item_name, attr_list, danger_mode)

        for key in attributes:
            if attrs[key] == None:
                try:
                    attrs[key] = default_values[key]
                except TypeError:
                    raise KeyError('Attribute \'{}\' of item \'{}\' cannot be updated because it does not exist and it has no default value set. Set a default value with the default_values parameter, or handle this error on your own.'.format(key, item_name))

            await usr_inventory.set_raw('Inventory', item_name, *self._check_danger(danger_mode), key, value = attrs[key] + attributes[key])
            attrs[key] = attrs[key] + attributes[key]

        return attrs

    
    """ Allows a user to check weapon charges."""
    @commands.command()  
    async def charges(self, ctx, *, weaponname):
        weaponname = weaponname.title()
        events = ctx.bot.get_cog('Events')
        data = await events.import_json()
        # Checks if item is a weapon.
        weapons = data['items']
        if weaponname not in weapons.keys():
            return await ctx.send("This is not a weapon.")

        base_charges = data['base_values']['Charges']
        weaponemoji = data['items'][weaponname]['Emoji']

        try:
            item_attr = await self.get_attr(ctx, ctx.author, weaponname, ['charges'])
        except KeyError:
            return await ctx.send("You do not own this item!")
        item_charges = item_attr['charges']
        if item_charges is None:
            item_charges = base_charges
            
        return await ctx.send("{} charges: {}".format(weaponemoji, item_charges))
        



    # helper function to clean up argument controls
    # checks if a user has an item in their inventory and will throw an error if they don't
    # then returns the users inventory
    async def _get_check_inv(self, ctx, user: discord.Member, item_name):
        if user is None:
            user = ctx.author

        inventory = await self.get_instance(ctx, user=user)

        try:
            await inventory.get_raw('Inventory', item_name)
        except KeyError as err:
            raise KeyError('User doesn\'t have \'{}\' item in their inventory'.format(item_name))

        return inventory

    # simple helper for cleaning up argument controls
    # makes *args easy
    def _check_danger(self, danger_mode=False):
        danger_path = []
        if not danger_mode:
            danger_path = ['Attributes']
        return danger_path



    @commands.command()
    async def inventory(self, ctx):
        """Displays your purchased items."""
        try:
            instance = await self.get_instance(ctx, user=ctx.author)
        except AttributeError:
            return await ctx.send("You can't use this command in pm when not in global mode.")
        if not await instance.Inventory():
            return await ctx.send("You don't have any items to display.")
        data = await instance.Inventory.all()
        menu = Inventory(ctx, list(data.items()))

        try:
            item = await menu.display()
        except RuntimeError:
            return
        await self.pending_prompt(ctx, instance, data, item)

    async def inv_hook(self, user):
        """Inventory Hook for outside cogs

        Parameters
        ----------
        user : discord.Member or discord.User

        Returns
        -------
        dict
            Returns a dict of the user's inventory or empty if the user
            is not found.
        """
        try:
            instance = await self._inv_hook_instance(user)
        except AttributeError:
            return {}
        else:
            return await instance.Inventory.all()

    async def _inv_hook_instance(self, user):
        if await self.db.Global():
            return self.db.user(user)
        else:
            return self.db.member(user)

    @commands.group(autohelp=True)
    async def shop(self, ctx):
        """Shop group command"""
        pass

    @shop.command()
    async def buy(self, ctx, *purchase):
        """Shop menu appears with no purchase order.

        When no argument is specified for purchase, it will bring up the
        shop menu.

        Using the purchase argument allows direct purchases from a shop.
        The order is `Shop Name, Item Name` and names with spaces
        must include quotes.

        Examples
        --------
        [p]shop buy \"Secret Shop\" oil
        [p]shop buy Junkyard tire
        [p]shop buy \"Holy Temple\" \"Healing Potion\"
        """
        instance = await self.get_instance(ctx, settings=True)
        if not await instance.Shops():
            return await ctx.send("No shops have been created yet.")
        if await instance.Settings.Closed():
            return await ctx.send("The shop system is currently closed.")

        shops = await instance.Shops.all()
        col = await self.check_availability(ctx, shops)
        if not col:
            return await ctx.send("Either no items have been created, or you need a "
                                  "higher role.")
        if purchase:
            try:
                shop, item = purchase
            except ValueError:
                return await ctx.send("Too many parameters passed. Use help on this command for "
                                      "more information.")
            if shop not in shops:
                return await ctx.send("Either that shop does not exist, or you don't have access "
                                      "to it.")

        else:
            menu = ShopMenu(ctx, shops)
            try:
                shop, item = await menu.display()
            except RuntimeError:
                return

        user_data = await self.get_instance(ctx, user=ctx.author)
        sm = ShopManager(ctx, instance, user_data)
        try:
            await sm.order(shop, item)
        except asyncio.TimeoutError:
            await ctx.send("Request timed out.")

    @shop.command()
    async def redeem(self, ctx, *, item: str):
        """Redeems an item in your inventory."""
        instance = await self.get_instance(ctx, user=ctx.author)
        data = await instance.Inventory.all()
        if data is None:
            return await ctx.send("Your inventory is empty.")

        if item not in data:
            return await ctx.send("You don't own this item.")
        
        customitems = ctx.bot.get_cog('CustomItems')
        await customitems.redeem_item(ctx, item)
        #await self.pending_prompt(ctx, instance, data, item)

        
    
    async def item_remove(self, ctx, item):
        user_instance = await self.get_instance(ctx, user=ctx.author)
        sm = ShopManager(ctx, None, user_instance)
        # sm = ShopManager(ctx, instance=None, user_data=instance)
        await sm.remove(item)
    
    @shop.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def trade(self, ctx, user: discord.Member, quantity: int, *, item: str):
        """Attempts to trade an item with another user.

        Cooldown is a static 60 seconds to prevent abuse.
        Cooldown will trigger regardless of the outcome.
        """
        cancel = ctx.prefix + "cancel"
        author_instance = await self.get_instance(ctx, user=ctx.author)
        author_inventory = await author_instance.Inventory.all()
        user_instance = await self.get_instance(ctx, user=user)
        user_inv = await user_instance.Inventory.all()

        if not await user_instance.Trading():
            return await ctx.send("This user has trading turned off.")

        if item not in author_inventory:
            return await ctx.send("You don't own that item.")

        if 0 < author_inventory[item]['Qty'] < quantity:
            return await ctx.send("You don't have that many {}".format(item))

        await ctx.send("{} has requested a trade with {}.\n"
                       "They are offering {}x {}.\n Do wish to trade?\n"
                       "*This trade can be canceled at anytime by typing `{}`.*"
                       "".format(ctx.author.mention, user.mention, quantity, item, cancel))

        def check(m):
            return (m.author == user and m.content.lower() in ('yes', 'no', cancel)) or \
                   (m.author == ctx.author and m.content.lower() == cancel)

        try:
            decision = await ctx.bot.wait_for('message', timeout=25, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("Trade request timed out. Canceled trade.")

        if decision.content.lower() in ('no', cancel):
            return await ctx.send("Trade canceled.")
        await ctx.send("{} What is your counter offer?\n"
                       "*Example: 3 \"Healing Potions\"*".format(user.mention))

        def predicate(m):
            if m.author in (user, ctx.author) and m.content == cancel:
                return True
            if m.author != user:
                return False
            try:
                q, i = [x.strip() for x in m.content.split('"')[:2] if x]
            except ValueError:
                return False
            else:
                if i not in user_inv:
                    return False
                return 0 < user_inv[i]['Qty'] <= int(q)

        try:
            offer = await ctx.bot.wait_for('message', timeout=25, check=predicate)
        except asyncio.TimeoutError:
            return await ctx.send("Trade request timed out. Canceled trade.")
        if offer.content.lower() == cancel:
            return await ctx.send("Trade canceled.")
        qty, item2 = [x.strip() for x in offer.content.split('"')[:2] if x]
        await ctx.send("{} Do you wish to trade {}x {} for {}'s {}x {}?"
                       "".format(ctx.author.mention, quantity, item, user.mention, qty, item2))

        def check2(m):
            return (m.author == ctx.author and m.content.lower() in ('yes', 'no', cancel)) or \
                   (m.author == user and m.content.lower() == cancel)
        try:
            final = await ctx.bot.wait_for('message', timeout=25, check=check2)
        except asyncio.TimeoutError:
            return await ctx.send("Trade request timed out. Canceled trade.")

        if final.content.lower() in ('no', cancel):
            return await ctx.send("Trade canceled.")

        sm1 = ShopManager(ctx, instance=None, user_data=author_instance)
        await sm1.add(item2, user_inv[item2], int(qty))
        await sm1.remove(item, number=quantity)

        sm2 = ShopManager(ctx, instance=None, user_data=user_instance)
        await sm2.add(item, author_inventory[item], quantity)
        await sm2.remove(item2, number=int(qty))

        await ctx.send("Trade complete.")

    @shop.command()
    async def tradetoggle(self, ctx):
        """Disables or enables trading with you."""
        instance = await self.get_instance(ctx, user=ctx.author)
        status = await instance.Trading()
        await instance.Trading.set(not status)
        await ctx.send("Trading with you is now {}.".format("disabled" if status else "enabled"))

    @shop.command()
    async def version(self, ctx):
        """Shows the current Shop version."""
        await ctx.send("Shop is running version {}.".format(__version__))

    @shop.command()
    @commands.is_owner()
    async def wipe(self, ctx):
        """Wipes all shop cog data."""
        await ctx.send("You are about to delete all shop and user data from the bot. Are you "
                       "sure this is what you wish to do?")

        try:
            choice = await ctx.bot.wait_for('message', timeout=25.0, check=Checks(ctx).confirm)
        except asyncio.TimeoutError:
            return await ctx.send("No Response. Action canceled.")

        if choice.content.lower() == 'yes':
            await self.db.clear_all()
            msg = "{0.name} ({0.id}) wiped all shop data.".format(ctx.author)
            log.info(msg)
            await ctx.send(msg)
        else:
            return await ctx.send("Wipe canceled.")

    @shop.command()
    @global_permissions()
    @guild_required_or_global()
    async def pending(self, ctx):
        """Displays the pending menu."""
        instance = await self.get_instance(ctx, settings=True)
        if not await instance.Pending():
            return await ctx.send("There are not any pending items.")
        data = await instance.Pending.all()
        menu = ShopMenu(ctx, data, mode=1)

        try:
            user, item, = await menu.display()
        except RuntimeError:
            return

        try:
            await self.clear_single_pending(ctx, instance, data, item, user)
        except asyncio.TimeoutError:
            await ctx.send("Request timed out.")

    @shop.command()
    @global_permissions()
    @guild_required_or_global()
    async def give(self, ctx, user: discord.Member, quantity: int, *shopitem):
        """Gives a user an item.

        Shopitem argument must be a \"Shop Name\" \"Item Name\" format.

        The item must be in the shop in order for this item to be given.
        Only basic and role items can be given.
        Giving a user an item does not affect the stock in the shop.

        Examples
        --------
        [p]shop give Redjumpman 1 "Holy Temple" "Healing Potion"
        [p]shop give Redjumpman 1 Junkyard Scrap
        """
        if quantity < 1:
            return await ctx.send(":facepalm: You can't do that.")

        if shopitem is None:
            return await ctx.send_help()

        try:
            shop, item = shopitem
        except ValueError:
            return await ctx.send("Must be a `\"Shop Name\" \"Item Name\"` format.")

        instance = await self.get_instance(ctx, settings=True)
        shops = await instance.Shops.all()
        if shop not in shops:
            return await ctx.send("Invalid shop name.")
        elif item not in shops[shop]['Items']:
            return await ctx.send("That item in not in the {} shop.".format(shop))
        elif shops[shop]['Items'][item]['Type'] not in ('basic', 'role'):
            return await ctx.send("You can only give basic or role type items.")
        else:
            data = deepcopy(shops[shop]['Items'][item])
            user_instance = await self.get_instance(ctx, user=user)
            sm = ShopManager(ctx, None, user_instance)
            await sm.add(item, data, quantity)
            await ctx.send("{} just gave {} a {}.".format(ctx.author.mention, user.mention, item))

    @shop.command()
    @global_permissions()
    @guild_required_or_global()
    async def clearinv(self, ctx, user: discord.Member):
        """Completely clears a user's inventory."""
        await ctx.send("Are you sure you want to completely wipe {}'s inventory?".format(user.name))
        choice = await ctx.bot.wait_for('message', timeout=25, check=Checks(ctx).confirm)
        if choice.content.lower() != 'yes':
            return await ctx.send("Canceled inventory wipe.")
        instance = await self.get_instance(ctx=ctx, user=user)
        await instance.Inventory.clear()
        await ctx.send("Done. Inventory wiped for {}.".format(user.name))

    @shop.command()
    @global_permissions()
    @guild_required_or_global()
    async def manager(self, ctx, action: str):
        """Creates edits, or deletes a shop."""
        if action.lower() not in ('create', 'edit', 'delete'):
            return await ctx.send("Action must be create, edit, or delete.")
        instance = await self.get_instance(ctx, settings=True)
        try:
            if action.lower() == 'create':
                await self.create_shop(ctx, instance)
            elif action.lower() == 'edit':
                await self.edit_shop(ctx, instance)
            else:
                await self.delete_shop(ctx, instance)
        except asyncio.TimeoutError:
            await ctx.send("Shop manager timed out.")

    @shop.command()
    @global_permissions()
    @guild_required_or_global()
    async def item(self, ctx, action: str):
        """Creates, Deletes, and Edits items."""
        if action.lower() not in ('create', 'edit', 'delete'):
            return await ctx.send("Must pick create, edit, or delete.")
        instance = await self.get_instance(ctx, settings=True)
        im = ItemManager(ctx, instance)
        try:
            await im.run(action)
        except asyncio.TimeoutError:
            return await ctx.send("Request timed out. Process canceled.")

    @shop.command()
    @global_permissions()
    @guild_required_or_global()
    async def restock(self, ctx, amount: int, *, shop_name: str):
        """Restocks all items in a shop by a specified amount.

        This command will not restock auto items, because they are required
        to have an equal number of messages and stock.
        """
        instance = await self.get_instance(ctx, settings=True)
        shop = shop_name
        if shop not in await instance.Shops():
            return await ctx.send("That shop does not exist.")
        await ctx.send("Are you sure you wish to increase the quantity of all "
                       "items in {} by {}?\n*Note, this won't affect auto items.*"
                       "".format(shop, amount))
        try:
            choice = await ctx.bot.wait_for('message', timeout=25, check=Checks(ctx).confirm)
        except asyncio.TimeoutError:
            return await ctx.send("Response timed out.")

        if choice.content.lower() == 'yes':
            async with instance.Shops() as shops:
                for item in shops[shop]['Items'].values():
                    if item['Type'] != 'auto':
                        try:
                            item['Qty'] += amount
                        except TypeError:
                            continue
            await ctx.send("All items in {} have had their quantities increased by {}."
                           "".format(shop, amount))
        else:
            await ctx.send("Restock canceled.")

    @shop.command()
    @global_permissions()
    @guild_required_or_global()
    async def bulkadd(self, ctx, style: str, *, entry: str):
        """Add multiple items and shops.

        Bulk accepts two styles: text or a file. If you choose
        file, then the next argument is your file name.

        Files should be saved in your CogManager/cogs/shop/data path.

        If you choose text, then each line will be parsed.
        Each entry begins as a new line. All parameters MUST
        be separated by a comma.

        Parameters:
        ----------
        Shop Name, Item Name, Type, Quantity, Cost, Info, Role
        Role is only required if the type is set to role.

        Examples
        -------
        Holy Temple, Torch, basic, 20, 5, Provides some light.
        Holy Temple, Divine Training, role, 20, 500, Gives Priest role., Priest
        Junkyard, Mystery Box, random, 20, 500, Random piece of junk.

        For more information on the parameters visit the shop wiki.
        """
        if style.lower() not in ('file', 'text'):
            return await ctx.send('Invalid style type. Must be file or text.')

        msg = await ctx.send("Beginning bulk upload process for shop. This may take a while...")
        instance = await self.get_instance(ctx, settings=True)
        parser = Parser(ctx, instance, msg)
        if style.lower() == 'file':
            data_path = cog_data_path()
            fp = os.path.join(data_path, 'CogManager', 'cogs', 'shop', 'data', entry + '.csv')
            await parser.search_csv(fp)
        else:
            await parser.parse_text_entry(entry)

    # -----------------------------------------------------------------------------

    @commands.group(autohelp=True)
    async def setshop(self, ctx):
        """Shop Settings group command"""
        pass

    @setshop.command()
    @commands.is_owner()
    async def mode(self, ctx):
        """Toggles Shop between global and local modes.

        When shop is set to local mode, each server will have its own
        unique data, and admin level commands can be used on that server.

        When shop is set to global mode, data is linked between all servers
        the bot is connected to. In addition, admin level commands can only be
        used by the owner or co-owners.
        """
        author = ctx.author
        mode = 'global' if await self.shop_is_global() else 'local'
        alt = 'local' if mode == 'global' else 'global'
        await ctx.send("Shop is currently set to {} mode. Would you like to change to {} "
                       "mode instead?".format(mode, alt))
        checks = Checks(ctx)
        try:
            choice = await ctx.bot.wait_for('message', timeout=25.0, check=checks.confirm)
        except asyncio.TimeoutError:
            return await ctx.send("No response. Action canceled.")

        if choice.content.lower() != 'yes':
            return await ctx.send("Shop will remain {}.".format(mode))
        await ctx.send("Changing shop to {0} will **DELETE ALL** current shop data. Are "
                       "you sure you wish to make shop {0}?".format(alt))
        try:
            final = await ctx.bot.wait_for('message', timeout=25.0, check=checks.confirm)
        except asyncio.TimeoutError:
            return await ctx.send("No response. Action canceled.")

        if final.content.lower() == 'yes':
            await self.change_mode(alt)
            log.info("{} ({}) changed the shop mode to {}.".format(author.name, author.id, alt))
            await ctx.send("Shop data deleted! Shop mode is now set to {}.".format(alt))
        else:
            await ctx.send("Shop will remain {}.".format(mode))

    @setshop.command()
    @global_permissions()
    @guild_required_or_global()
    async def alertrole(self, ctx, role: discord.Role):
        """Sets the role that will receive alerts.

        Alerts will be sent to any user who has this role on the server. If
        the shop is global, then the owner will receive alerts regardless
        of their role, until they turn off alerts.
        """
        if role.name == 'Bot':
            return
        instance = await self.get_instance(ctx, settings=True)
        await instance.Settings.Alert_Role.set(role.name)
        await ctx.send("Alert role has been set to {}.".format(role.name))

    @setshop.command()
    @global_permissions()
    @guild_required_or_global()
    async def alerts(self, ctx):
        """Toggles alerts when users redeem items."""
        instance = await self.get_instance(ctx, settings=True)
        status = await instance.Settings.Alerts()
        await instance.Settings.Alerts.set(not status)
        await ctx.send("Alert role will {} messages.".format("no longer" if status else "receive"))

    @setshop.command()
    @global_permissions()
    @guild_required_or_global()
    async def toggle(self, ctx):
        """Closes/opens all shops."""
        instance = await self.get_instance(ctx, settings=True)
        status = await instance.Settings.Closed()
        await instance.Settings.Closed.set(not status)
        await ctx.send("Shops are now {}.".format("open" if status else "closed"))

    # -------------------------------------------------------------------------------

    @staticmethod
    async def check_availability(ctx, shops):
        perms = ctx.author.guild_permissions.administrator
        author_roles = [r.name for r in ctx.author.roles]
        return [x for x, y in shops.items() if (y['Role'] in author_roles or perms) and y['Items']]

    @staticmethod
    async def clear_single_pending(ctx, instance, data, item, user):
        item_name = data[str(user.id)][item]['Item']
        await ctx.send("You are about to clear a pending {} for {}.\nAre you sure "
                       "you wish to clear this item?".format(item_name, user.name))
        choice = await ctx.bot.wait_for('message', timeout=25, check=Checks(ctx).confirm)
        if choice.content.lower() == 'yes':
            async with instance.Pending() as p:
                del p[str(user.id)][item]
                if not p[str(user.id)]:
                    del p[str(user.id)]
            await ctx.send('{} was cleared from {}\'s pending by {}.'.format(item_name, user.name,
                                                                             ctx.author.name))
            await user.send("{} cleared your pending {}!".format(ctx.author.name, item_name))
        else:
            await ctx.send("Action canceled.")

    @staticmethod
    async def clear_all_pending(ctx, instance, user):
        await ctx.send("You are about to clear all pending items from {}.\n"
                       "Are you sure you wish to do this?")
        choice = await ctx.bot.wait_for('message', timeout=25, check=Checks(ctx).confirm)
        if choice.content.lower() == 'yes':
            async with instance.Pending() as p:
                del p[user.id]
            await ctx.send("All pending items have been cleared for {}.".format(user.name))
            await user.send("{} cleared **ALL** of your pending items.".format(ctx.author.name))
        else:
            await ctx.send("Action canceled.")

    async def get_instance(self, ctx, settings=False, user=None):
        if not user:
            user = ctx.author

        if await self.db.Global():
            if settings:
                return self.db
            else:
                return self.db.user(user)
        else:
            if settings:
                return self.db.guild(ctx.guild)
            else:
                return self.db.member(user)

    async def assign_role(self, ctx, instance, item, role_name):
        if await self.db.Global():
            await ctx.send("Unable to assign role, because shop is in global mode.")

        role = discord.utils.get(ctx.message.guild.roles, name=role_name)
        if role is None:
            await ctx.send("Could not assign the role, {}, because it does not exist "
                           "on the server.".format(role_name))
        try:
            await ctx.author.add_roles(role, reason='Shop role token was redeemed.')
        except discord.Forbidden:
            await ctx.send("The bot could not add this role because it does not have the "
                           "permission to do so. Make sure the bot has the permissions enabled and "
                           "its role is higher than the role that needs to be assigned.")
            return False
        sm = ShopManager(ctx, None, instance)
        await sm.remove(item)
        await ctx.send("{} was granted the {} role.".format(ctx.author.mention, role.name))

    async def pending_add(self, ctx, item):
        instance = await self.get_instance(ctx, settings=True)
        unique_id = str(uuid.uuid4())[:17]
        timestamp = ctx.message.created_at.now().strftime('%Y-%m-%d %H:%M:%S')
        async with instance.Pending() as p:
            if str(ctx.author.id) in p:
                p[str(ctx.author.id)][unique_id] = {'Item': item, 'Timestamp': timestamp}
            else:
                p[str(ctx.author.id)] = {unique_id: {'Item': item, 'Timestamp': timestamp}}
        msg = "{} added {} to your pending list.".format(ctx.author.mention, item)
        if await instance.Settings.Alerts():
            alert_role = await instance.Settings.Alert_Role()
            role = discord.utils.get(ctx.guild.roles, name=alert_role)
            if role:
                msg = "{}\n{}".format(role.mention, msg)
        await ctx.send(msg)

    async def change_mode(self, mode):
        await self.db.clear_all()
        if mode == 'global':
            await self.db.Global.set(True)

    async def shop_is_global(self):
        return await self.db.Global()

    async def edit_shop(self, ctx, instance):
        shops = await instance.Shops.all()
        await ctx.send("What shop would you like to edit?")
        name = await ctx.bot.wait_for('message', timeout=25,
                                      check=Checks(ctx, custom=shops).content)

        await ctx.send("Would you like to change the shop's `name` or `role` requirement?")
        choice = await ctx.bot.wait_for('message', timeout=25,
                                        check=Checks(ctx, custom=('name', 'role')).content)
        if choice.content.lower() == 'name':
            await ctx.send("What is the new name for this shop?")
            new_name = await ctx.bot.wait_for('message', timeout=25,
                                              check=Checks(ctx, length=25).length_under)
            async with instance.Shops() as shops:
                shops[new_name.content] = shops.pop(name.content)
            return await ctx.send("Name changed to {}.".format(new_name.content))
        else:
            await ctx.send("What is the new role for this shop?")
            role = await ctx.bot.wait_for('message', timeout=25, check=Checks(ctx).role)
            async with instance.Shops() as shops:
                shops[name.content]['Role'] = role.content
            await ctx.send("{} is now restricted to only users "
                           "with the {} role.".format(name.content, role.content))

    async def delete_shop(self, ctx, instance):
        shops = await instance.Shops.all()
        await ctx.send("What shop would you like to delete?")
        name = await ctx.bot.wait_for('message', timeout=25,
                                      check=Checks(ctx, custom=shops).content)
        await ctx.send("Are you sure you wish to delete {} and all of its "
                       "items?".format(name.content))
        choice = await ctx.bot.wait_for('message', timeout=25, check=Checks(ctx).confirm)

        if choice.content.lower() == 'no':
            return await ctx.send("Shop deletion canceled.")
        async with instance.Shops() as shops:
            del shops[name.content]
        await ctx.send("{} was deleted.".format(name.content))

    async def create_shop(self, ctx, instance):
        await ctx.send("What is the name of this shop?\nName must be 25 characters or less.")
        name = await ctx.bot.wait_for('message', timeout=25,
                                      check=Checks(ctx, length=25).length_under)

        if name.content in await instance.Shops():
            return await ctx.send("A shop with this name already exists.")

        await ctx.send("What role can use this shop? Use `all` for everyone.\n"
                       "*Note: this role must exist on this server and is "
                       "case sensitive.*")

        def predicate(m):
            if m.author == ctx.author:
                if m.content in [r.name for r in ctx.guild.roles]:
                    return True
                elif m.content.lower() == 'all':
                    return True
                else:
                    return False
            else:
                return False

        try:
            role = await ctx.bot.wait_for('message', timeout=25.0, check=predicate)
        except asyncio.TimeoutError:
            return await ctx.send("Response timed out. Shop creation ended.")

        role_name = role.content if role.content != 'all' else '@everyone'
        async with instance.Shops() as shops:
            shops[name.content] = {'Items': {}, 'Role': role_name}
        await ctx.send("Added {} to the list of shops.\n"
                       "**NOTE:** This shop will not show up until an item is added to it's "
                       "list.".format(name.content))

    async def pending_prompt(self, ctx, instance, data, item):
        if data[item]['Type'].lower() == 'Role':
            await ctx.send("Do you wish to redeem {}? This will grant you the role assigned to "
                           "this item and it will be removed from your inventory "
                           "premenantly.".format(item))
        else:
            await ctx.send("Do you wish to redeem {}? This will add the item to the pending list "
                           "for an admin to review and grant. The item will be removed from your "
                           "inventory while this is processing.".format(item))
        try:
            choice = await ctx.bot.wait_for('message', timeout=25, check=Checks(ctx).confirm)
        except asyncio.TimeoutError:
            return await ctx.send('No Response. Item redemption canceled.')

        if choice.content.lower() != 'yes':
            return await ctx.send('Canceled item redemption.')

        if data[item]['Type'].lower() == 'role':
            return await self.assign_role(ctx, instance, item, data[item]['Role'])
        else:
            await self.pending_add(ctx, item)

        sm = ShopManager(ctx, instance=None, user_data=instance)
        await sm.remove(item)
        
    async def get_user_inventory(self, instance):
        return await instance.Inventory.all()
        


class ShopManager:

    def __init__(self, ctx, instance, user_data):
        self.ctx = ctx
        self.instance = instance
        self.user_data = user_data

    @staticmethod
    def weighted_choice(choices):
        """Stack Overflow: https://stackoverflow.com/a/4322940/6226473"""
        values, weights = zip(*choices)
        total = 0
        cum_weights = []
        for w in weights:
            total += w
            cum_weights.append(total)
        x = random.random() * total
        i = bisect(cum_weights, x)
        return values[i]

    async def random_item(self, shop):
        async with self.instance.Shops() as shops:
            try:
                return self.weighted_choice([(x, y['Cost']) for x, y in shops[shop]['Items'].items()
                                             if y['Type'] != 'random'])
            except IndexError:
                return

    async def auto_handler(self, shop, item, amount):
        async with self.instance.Shops() as shops:
            msgs = [shops[shop]['Items'][item]['Messages'].pop() for _ in range(amount)]
        msg = '\n'.join(msgs)
        if len(msg) < 2000:
            await self.ctx.author.send(msg)
        else:
            chunks = textwrap.wrap(msg, 2000)
            for chunk in chunks:
                await asyncio.sleep(2)  # At least a little buffer to prevent rate limiting
                await self.ctx.author.send(chunk)

    async def order(self, shop, item):
        try:
            async with self.instance.Shops() as shops:
                item_data = deepcopy(shops[shop]['Items'][item])
        except KeyError:
            return await self.ctx.send("Could not locate that shop or item.")

        cur = await bank.get_currency_name(self.ctx.guild)
        stock, cost, _type = item_data['Qty'], item_data['Cost'], item_data['Type']

        await self.ctx.send("How many {} would you like to purchase?\n*If this "
                            "is a random item, you can only buy 1 at a time.*".format(item))

        def predicate(m):
            if m.author == self.ctx.author and m.content.isdigit():
                if _type == 'random':
                    return int(m.content) == 1
                try:
                    return 0 < int(m.content) <= stock
                except TypeError:
                    return 0 < int(m.content)
            else:
                return False
        num = await self.ctx.bot.wait_for('message', timeout=25.0, check=predicate)
        amount = int(num.content)
        try:
            await num.delete()
        except discord.NotFound:
            pass

        cost *= amount
        try:
            await bank.withdraw_credits(self.ctx.author, cost)
        except ValueError:
            return await self.ctx.send("You cannot afford {}x {} for {} {}. Transaction "
                                       "ended.".format(num.content, item, cost, cur))
        im = ItemManager(self.ctx, self.instance)
        if _type == 'auto':
            await self.auto_handler(shop, item, amount)
            await im.remove(shop, item, stock, amount)
            return await self.ctx.send("Message sent.")

        if _type == 'random':
            new_item = await self.random_item(shop)
            if new_item is None:
                await bank.deposit_credits(self.ctx.author, cost)
                return await self.ctx.send("There aren't any non-random items available in {}, "
                                           "so {} cannot be purchased.".format(shop, item))
            else:
                await im.remove(shop, item, stock, amount)
                item = new_item
                async with self.instance.Shops() as shops:
                    item_data = deepcopy(shops[shop]['Items'][new_item])
                stock = item_data['Qty']

        await im.remove(shop, item, stock, amount)
        await self.add(item, item_data, amount)
        await self.ctx.send("{} purchased {}x {} for {} {}."
                            "".format(self.ctx.author.mention, amount, item, cost, cur))

    async def add(self, item, data, quantity):
        async with self.user_data.Inventory() as inv:
            if item in inv:
                inv[item]['Qty'] += quantity
            else:
                inv[item] = data
                inv[item]['Qty'] = quantity

    async def remove(self, item, number=1):
        async with self.user_data.Inventory() as inv:
            if number >= inv[item]['Qty']:
                del inv[item]
            else:
                inv[item]['Qty'] -= number


class ItemManager:

    def __init__(self, ctx, instance):
        self.ctx = ctx
        self.instance = instance

    async def run(self, action):

        if action.lower() == "create":
            await self.create()
        elif action.lower() == "edit":
            await self.edit()
        else:
            await self.delete()

    async def create(self):
        name = await self.set_name()
        cost = await self.set_cost()
        info = await self.set_info()
        _type, role, msgs = await self.set_type()
        if _type != 'auto':
            qty = await self.set_quantity(_type)
        else:
            qty = len(msgs)

        data = {'Cost': cost, 'Qty': qty, 'Type': _type, 'Info': info, 'Role': role,
                'Messages': msgs}

        await self.ctx.send("What shop would you like to add this item to?")
        shops = await self.instance.Shops()
        shop = await self.ctx.bot.wait_for('message', timeout=25,
                                           check=Checks(self.ctx, custom=shops.keys()).content)
        await self.add(data, shop.content, name)
        await self.ctx.send("Item creation complete. Check your logs to ensure it went to the "
                            "approriate shop.")

    async def delete(self):
        shop_list = await self.instance.Shops.all()

        def predicate(m):
            if self.ctx.author != m.author:
                return False
            return m.content in shop_list

        await self.ctx.send("What shop would you like to delete an item from?")
        shop = await self.ctx.bot.wait_for('message', timeout=25, check=predicate)

        def predicate2(m):
            if self.ctx.author != m.author:
                return False
            return m.content in shop_list[shop.content]['Items']

        await self.ctx.send("What item would you like to delete from this shop?")
        item = await self.ctx.bot.wait_for('message', timeout=25, check=predicate2)
        await self.ctx.send("Are you sure you want to delete {} from {}?".format(item.content,
                                                                                 shop.content))
        choice = await self.ctx.bot.wait_for('message', timeout=25, check=Checks(self.ctx).confirm)
        if choice.content.lower() == 'yes':
            async with self.instance.Shops() as shops:
                del shops[shop.content]['Items'][item.content]
            await self.ctx.send("{} was deleted from the {}.".format(item.content, shop.content))
        else:
            await self.ctx.send("Item deletion canceled.")

    async def edit(self):
        choices = ('name', 'type', 'role', 'qty', 'cost', 'msgs', 'quantity', 'messages')

        while True:
            shop, item, item_data = await self.get_item()

            def predicate(m):
                if self.ctx.author != m.author:
                    return False
                if m.content.lower() in ('msgs', 'messages') and item_data['Type'] != 'auto':
                    return False
                elif m.content.lower() in ('qty', 'quantity') and item_data['Type'] == 'auto':
                    return False
                elif m.content.lower() == 'role' and item_data['Type'] != 'role':
                    return False
                elif m.content.lower() not in choices:
                    return False
                else:
                    return True

            await self.ctx.send("What would you like to edit for this item?\n"
                                "Name, Type, Role, Quantity, Cost, Messages")
            choice = await self.ctx.bot.wait_for('message', timeout=25.0, check=predicate)

            if choice.content.lower() == 'name':
                await self.set_name(item=item, shop=shop)
            elif choice.content.lower() == 'type':
                await self.set_type(item, shop)
            elif choice.content.lower() == 'role':
                await self.set_role(item, shop)
            elif choice.content.lower() in ('qty', 'quantity'):
                await self.set_quantity(item_data['Type'], item, shop)
            elif choice.content.lower() == 'cost':
                await self.set_cost(item=item, shop=shop)
            else:
                await self.set_messages(item_data['Type'], item=item, shop=shop)

            await self.ctx.send("Would you like to continue editing?")
            rsp = await self.ctx.bot.wait_for('message', timeout=25, check=Checks(self.ctx).confirm)
            if rsp.content.lower() == 'no':
                await self.ctx.send("Editing process exited.")
                break

    async def set_messages(self, _type, item=None, shop=None):
        if _type != 'auto':
            return await self.ctx.send("You can only add messages to auto type items.")
        await self.ctx.send("Auto items require a message to be stored per quantity. Separate each "
                            "message with a new line using a code block.")
        msgs = await self.ctx.bot.wait_for('message', timeout=120, check=Checks(self.ctx).same)
        auto_msgs = [x.strip() for x in msgs.content.strip('`').split('\n') if x]
        if item:
            async with self.instance.Shops() as shops:
                shops[shop]['Items'][item]['Messages'].extend(auto_msgs)
                shops[shop]['Items'][item]['Qty'] += len(auto_msgs)
            return await self.ctx.send("{} messages were added to {}."
                                       "".format(len(auto_msgs), item))
        return auto_msgs

    async def set_name(self, item=None, shop=None):
        await self.ctx.send("Enter a name for this item. It can't be longer than 15 characters.")
        name = await self.ctx.bot.wait_for('message', timeout=25,
                                           check=Checks(self.ctx, length=15).length_under)
        if item:
            async with self.instance.Shops() as shops:
                shops[shop]['Items'][name.content] = shops[shop]['Items'].pop(item)
            return await self.ctx.send("{}'s name was changed to {}.".format(item, name.content))
        return name.content

    async def set_cost(self, item=None, shop=None):
        await self.ctx.send('Enter the new cost for this item.')
        cost = await self.ctx.bot.wait_for('message', timeout=25, check=Checks(self.ctx).positive)

        if item:
            async with self.instance.Shops() as shops:
                shops[shop]['Items'][item]['Cost'] = int(cost.content)
            return await self.ctx.send("This item now costs {}.".format(cost.content))
        return int(cost.content)

    async def set_role(self, item=None, shop=None):
        await self.ctx.send("What role do you wish for this item to assign?")
        role = await self.ctx.bot.wait_for('message', timeout=25, check=Checks(self.ctx).role)
        if item:
            async with self.instance.Shops() as shops:
                shops[shop]['Items'][item]['Role'] = role.content
            return await self.ctx.send("This item now assigns the {} role.".format(role.content))
        return role.content

    async def set_quantity(self, _type=None, item=None, shop=None):
        if _type == 'auto':
            return await self.ctx.send("You can't change the quantity of an auto item. The "
                                       "quantity will match the messages set.")

        await self.ctx.send("What quantity do you want to set this item to?\n"
                            "Type 0 for infinite.")

        def check(m):
            return m.author == self.ctx.author and m.content.isdigit() and int(m.content) >= 0

        qty = await self.ctx.bot.wait_for('message', timeout=25, check=check)
        qty = int(qty.content) if int(qty.content) > 0 else '--'
        if item:
            async with self.instance.Shops() as shops:
                shops[shop]['Items'][item]['Qty'] = qty
            return await self.ctx.send("Quantity for {} now set to "
                                       "{}.".format(item, 'infinite.' if qty == '--' else qty))
        return qty

    async def set_type(self, item=None, shop=None):
        valid_types = ('basic', 'random', 'auto', 'role')
        await self.ctx.send("What is the item type?\n"
                            "basic  - Normal item and is added to the pending list when redeemed.\n"
                            "random - Picks a random item in the shop, weighted on cost.\n"
                            "role   - Grants a role when redeemed.\n"
                            "auto   - DM's a msg to the user instead of adding to their inventory.")
        _type = await self.ctx.bot.wait_for('message', timeout=25,
                                            check=Checks(self.ctx, custom=valid_types).content)

        if _type.content.lower() == 'auto':
            msgs = await self.set_messages('auto', item=item, shop=shop)
            if not item:
                return 'auto', None, msgs
        elif _type.content.lower() == 'role':
            role = await self.set_role(item=item, shop=shop)
            if not item:
                return 'role', role, None
        else:
            if item:
                async with self.instance.Shops() as shops:
                    shops[shop]['Items'][item]['Type'] = _type.content.lower()
                    try:
                        del shops[shop]['Items'][item]['Messages']
                        del shops[shop]['Items'][item]['Role']
                    except KeyError:
                        pass
                return await self.ctx.send("Item type set to {}.".format(_type.content.lower()))
            return _type.content.lower(), None, None
        async with self.instance.Shops() as shops:
            shops[shop]['Items'][item]['Type'] = _type.content.lower()

    async def set_info(self, item=None, shop=None):
        await self.ctx.send("Specify the info text for this item.\n"
                            "*Note* cannot be longer than 24 characters.")
        info = await self.ctx.bot.wait_for('message', timeout=40,
                                           check=Checks(self.ctx, length=24).length_under)
        if item:
            async with self.instance.Shops() as shops:
                shops[shop]['Items'][item]['Info'] = info.content
                return await self.ctx.send('Info now set to:\n{}'.format(info.content))
        return info.content

    async def get_item(self):
        shops = await self.instance.Shops.all()

        await self.ctx.send("What shop is the item you would like to edit in?")
        shop = await self.ctx.bot.wait_for('message', timeout=25.0,
                                           check=Checks(self.ctx, custom=shops).content)

        items = shops[shop.content]['Items']
        await self.ctx.send("What item would you like to edit?")
        item = await self.ctx.bot.wait_for('message', timeout=25.0,
                                           check=Checks(self.ctx, custom=items).content)

        return shop.content, item.content, shops[shop.content]['Items'][item.content]

    async def add(self, data, shop, item, new_allowed=False):
        async with self.instance.Shops() as shops:
            if shop not in shops:
                if new_allowed:
                    shops[shop] = {'Items': {item: data}, 'Role': '@everyone'}
                    return log.info('Created the shop: {} and added {}.'.format(shop, item))
                log.error('{} could not be added to {}, '
                          'because it does not exist.'.format(item, shop))
            elif item in shops[shop]["Items"]:
                log.error('{} was not added because that item already exists in {}.'
                          ''.format(item, shop))
            else:
                shops[shop]['Items'][item] = data
                log.info('{} added to {}.'.format(item, shop))

    async def remove(self, shop, item, stock, amount):
        try:
            remainder = stock - amount
            async with self.instance.Shops() as shops:
                if remainder > 0:
                    shops[shop]['Items'][item]['Qty'] = remainder
                else:
                    del shops[shop]['Items'][item]
        except TypeError:
            pass
        return
    
  


class Parser:
    def __init__(self, ctx, instance, msg):
        self.ctx = ctx
        self.instance = instance
        self.msg = msg

    @staticmethod
    def basic_checks(idx, row):
        if len(row['Shop']) > 25:
            log.warning("Row {} was not added because shop name was too long.".format(idx))
            return False
        elif len(row['Item']) > 15:
            log.warning("Row {} was not added because item name was too long.".format(idx))
            return False
        elif not row['Cost'].isdigit() or int(row['Cost']) < 0:
            log.warning("Row {} was not added because the cost was lower than 0.".format(idx))
            return False
        elif not row['Qty'].isdigit() or int(row['Qty']) < 0:
            log.warning("Row {} was not added because the quantity was lower than 0.".format(idx))
            return False
        elif len(row['Info']) > 24:
            log.warning("Row {} was not added because the info was too long.".format(idx))
            return False
        else:
            return True

    @staticmethod
    def type_checks(idx, row, messages):
        if row['Type'].lower() not in ('basic', 'random', 'auto', 'role'):
            log.warning("Row {} was not added because of an invalid type.".format(idx))
            return False
        elif row['Type'].lower() == 'role' and not row['Role']:
            log.warning("Row {} was not added because the type is a role, but no role was set"
                        ".".format(idx))
            return False
        elif row['Type'].lower() == 'auto' and int(row['Qty']) == 0:
            log.warning("Row {} was not added because auto items cannot have an infinite quantity."
                        "".format(idx))
            return False
        elif row['Type'].lower() == 'auto' and int(row['Qty']) != len(messages):
            log.warning("Row {} was not added because auto items must have an equal number of "
                        "messages and quantity.".format(idx))
            return False
        elif row['Type'].lower() == 'auto' and any(len(x) > 2000 for x in messages):
            log.warning("Row {} was not added because one of the messages exceeds 2000 characters."
                        "".format(idx))
            return False
        else:
            return True

    async def parse_text_entry(self, text):
        keys = ('Shop', 'Item', 'Type', 'Qty', 'Cost', 'Info', 'Role', 'Messages')
        raw_data = [[f.strip() for f in y] for y in
                    [x.split(',') for x in text.strip('`').split('\n') if x] if 6 <= len(y) <= 8]
        bulk = [{key: value for key, value in zip_longest(keys, x)} for x in raw_data]
        await self.parse_bulk(bulk)

    async def search_csv(self, file_path):
        try:
            with open(file_path, 'rt') as f:
                reader = csv.DictReader(f, delimiter=',')
                await self.parse_bulk(reader)
        except FileNotFoundError:
            await self.msg.edit(content='The specified filename could not be found.')

    async def parse_bulk(self, reader):
        if not reader:
            return await self.msg.edit(content="Data was faulty. No data was added.")

        keys = ('Cost', 'Qty', 'Type', 'Info', 'Role', 'Messages')
        for idx, row in enumerate(reader, 1):
            try:
                messages = [x.strip() for x in row['Messages'].split(',') if x]
            except AttributeError:
                messages = []

            if not self.basic_checks(idx, row):
                continue
            elif not self.type_checks(idx, row, messages):
                continue
            else:
                data = {key: row.get(key, None) if key not in ('Cost', 'Qty', 'Messages') else
                        int(row[key]) if key != 'Messages' else messages for key in keys}
                if data['Qty'] == 0:
                    data['Qty'] = '--'
                item_manager = ItemManager(self.ctx, self.instance)
                await item_manager.add(data, row['Shop'], row['Item'], new_allowed=True)
        await self.msg.edit(content="Bulk process finished. Please check your "
                                    "console for more information.")

    
class ExitProcess(Exception):
    pass
