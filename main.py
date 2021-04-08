import os
os.system("python3 webserver.py &")
import asyncio
import uvloop
import sys

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

try:
    from typing import Any, Union, Optional

    import asyncio
    import datetime
    import json
    import functools
    import random as py_random
    import subprocess

    from fortnitepy.ext import commands

    import aioconsole
    import crayons
    import fortnitepy
    import FortniteAPIAsync
    import sanic
    import aiohttp
except ModuleNotFoundError as e:
    print(f'Error: {e}\nAttempting to install packages now (this may take a while).')

    for module in (
        'crayons',
        'fortnitepy',
        'BenBotAsync',
        'FortniteAPIAsync',
        'uvloop',
        'sanic',
        'aiohttp',
        'aioconsole'
    ):
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

    os.system('clear')

    print('Installed packages, restarting script.')

    python = sys.executable
    os.execl(python, python, *sys.argv)



print(crayons.cyan(f'Discord server: https://discord.gg/EWdPpeps94 - For support, questions, etc.'))

sanic_app = sanic.Sanic(__name__)
server = None

name = ""

filename = 'device_auths.json'

@sanic_app.route('/', methods=['GET'])
async def accept_ping(request: sanic.request.Request) -> None:
    return sanic.response.json({"status": "online"})


@sanic_app.route('/name', methods=['GET'])
async def accept_ping(request: sanic.request.Request) -> None: # idk why this is green lol
    return sanic.response.json({"display_name": name})

def get_device_auth_details():
    if os.path.isfile(filename):
        with open(filename, 'r') as fp:
            return json.load(fp)
    return {}

def store_device_auth_details(email, details):
    existing = get_device_auth_details()
    existing[email] = details

    with open(filename, 'w') as fp:
        json.dump(existing, fp)

async def get_authorization_code():
    while True:
        response = await aioconsole.ainput("Go to https://rebrand.ly/authcode and sign in as "  + os.getenv("EMAIL") + " and enter the response: ")
        if "redirectUrl" in response:
            response = json.loads(response)
            if "?code" not in response["redirectUrl"]:
                print("Invalid response.")
                continue
            code = response["redirectUrl"].split("?code=")[1]
            return code
        else:
            if "https://accounts.epicgames.com/fnauth" in response:
                if "?code" not in response:
                    print("invalid response.")
                    continue
                code = response.split("?code=")[1]
                return code
            else:
                code = response
                return code

class SilverBot(commands.Bot):
    def __init__(self, email : str, password : str, **kwargs) -> None:
        self.status = os.getenv("STATUS")

        self.kairos = 'cid_028_ff2b06cf446376144ba408d3482f5c982bf2584cf0f508ee3e4ba4a0fd461a38'
        device_auth_details = get_device_auth_details().get(email, {})
        super().__init__(
            command_prefix=os.getenv("PREFIX"),
            auth=fortnitepy.AdvancedAuth(
                email=email,
                password=password,
                prompt_authorization_code=False,
                delete_existing_device_auths=True,
                authorization_code=get_authorization_code,
                **device_auth_details
            ),
            status=self.status,
            platform=fortnitepy.Platform(os.getenv("PLATFORM")),
            avatar=fortnitepy.Avatar(
                asset=self.kairos,
                background_colors=fortnitepy.KairosBackgroundColorPreset.PINK.value
            ),
            **kwargs
        )

        self.fortnite_api = FortniteAPIAsync.APIClient()
        self.loop = asyncio.get_event_loop()

        self.default_skin ="CID_NPC_Athena_Commando_M_Fallback"
        self.default_backpack = "BID_138_Celestial"
        self.default_pickaxe = os.getenv("PICKAXE")
        self.banner = "INFLUENCERBANNER27"
        self.banner_colour = "BID_138_Celestial"
        self.default_level = "666"
        self.default_bp_tier = "-666666666"
        self.default_emote = "EID_kpopdance03"

        self.sanic_app = sanic_app
        self.server = server
        self.welcome_message = "created Rikkoa bot by:g3_piton-52              bot Rikkoa creado por:g3_piton-52             create a lobby bot:https://discord.gg/EWdPpeps94               CREA TU PROPIO BOThttps://discord.gg/EWdPpeps94             twitch:skwox  YT:its moderator  Instagram:g3_ruben._.fuenla_     twiter:dekwik58       connect bot:16:60 a 21:00      frydays:9:00 a 23:00    my team fortnite Instagram:g3nesis_team     my code creator nosoypayaso✦🍣   check chat pls⃟"
        self.whisper_message = ""

    async def set_and_update_member_prop(self, schema_key: str, new_value: Any) -> None:
        prop = {schema_key: self.party.me.meta.set_prop(schema_key, new_value)}

        await self.party.me.patch(updated=prop)

    async def set_and_update_party_prop(self, schema_key: str, new_value: Any) -> None:
        prop = {schema_key: self.party.me.meta.set_prop(schema_key, new_value)}

        await self.party.patch(updated=prop)


    async def event_ready(self) -> None:
        global name

        name = self.user.display_name

        print(crayons.green(f'Client ready as {self.user.display_name}.'))

        coro = self.sanic_app.create_server(
            host='0.0.0.0',
            port=8000,
            return_asyncio_server=True,
            access_log=False
        )
        self.server = await coro

        for pending in self.incoming_pending_friends:
            epic_friend = await pending.accept()
            if isinstance(epic_friend, fortnitepy.Friend):
                print(f"Accepted friend request from: {epic_friend.display_name}.")
            else:
                print(f"Accepted friend request from: {pending.display_name}.")

    async def event_party_invite(self, invite: fortnitepy.ReceivedPartyInvitation) -> None:
        await invite.accept()
        print(f'Accepted party invite from {invite.sender.display_name}.')

    async def event_friend_request(self, request: fortnitepy.IncomingPendingFriend) -> None:
        print(f"Received friend request from: {request.display_name}.")

        await request.accept()
        print(f"Accepted friend request from: {request.display_name}.")

    async def event_party_member_join(self, member: fortnitepy.PartyMember) -> None:
        await self.party.send(self.welcome_message.replace('{DISPLAY_NAME}', member.display_name))

        if self.default_party_member_config.cls is not fortnitepy.party.JustChattingClientPartyMember:
            await self.party.me.edit(
                functools.partial(
                    self.party.me.set_outfit,
                    self.default_skin
                ),
                functools.partial(
                    self.party.me.set_backpack,
                    self.default_backpack
                ),
                functools.partial(
                    self.party.me.set_pickaxe,
                    self.default_pickaxe
                ),
                functools.partial(
                    self.party.me.set_banner,
                    icon=self.banner,
                    color=self.banner_colour,
                    season_level=self.default_level
                ),
                functools.partial(
                    self.party.me.set_battlepass_info,
                    has_purchased=True,
                    level=self.default_bp_tier
                )
            )

        

        if self.default_party_member_config.cls is not fortnitepy.party.JustChattingClientPartyMember:
            await self.party.me.clear_emote()
            await self.party.me.set_emote(asset=self.default_emote)

            if self.user.display_name != member.display_name:  # Welcomes the member who just joined.
                print(f"{member.display_name} has joined the lobby.")

    async def event_friend_message(self, message: fortnitepy.FriendMessage) -> None:
        print(f'{message.author.display_name}: {message.content}')
        await message.reply(self.welcome_message.replace('{DISPLAY_NAME}', message.author.display_name))

    async def event_command_error(self, ctx: fortnitepy.ext.commands.Context,
                                  error: fortnitepy.ext.commands.CommandError) -> None:
        if isinstance(error, fortnitepy.ext.commands.errors.CommandNotFound):
            if isinstance(ctx.message, fortnitepy.FriendMessage):
                await ctx.send('Command not found, are you sure it exists?')
            else:
                pass
        elif isinstance(error, fortnitepy.ext.commands.errors.MissingRequiredArgument):
            await ctx.send('Failed to execute commands as there are missing requirements, please check usage.')
        elif isinstance(error, fortnitepy.ext.commands.errors.PrivateMessageOnly):
            pass
        else:
            raise error

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client using the outfits name.",
        help="Sets the outfit of the client using the outfits name.\n"
             "Example: !skin Nog Ops"
    )
    async def skin(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="en",
                searchLang="en",
                matchMethod="contains",
                name=content,
                backendType="AthenaCharacter"
            )

            await ctx.send(f'Skin set to {cosmetic.id}.')
            print(f"Set skin to: {cosmetic.id}.")
            await self.party.me.set_outfit(asset=cosmetic.id)

        except FortniteAPIAsync.exceptions.NotFound:
            await ctx.send(f"Failed to find a skin with the name: {content}.")
            print(f"Failed to find a skin with the name: {content}.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the backpack of the client using the backpacks name.",
        help="Sets the backpack of the client using the backpacks name.\n"
             "Example: !backpack Black Shield"
    )
    async def backpack(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="en",
                searchLang="en",
                matchMethod="contains",
                name=content,
                backendType="AthenaBackpack"
            )

            await ctx.send(f'Backpack set to {cosmetic.id}.')
            print(f"Set backpack to: {cosmetic.id}.")
            await self.party.me.set_backpack(asset=cosmetic.id)

        except FortniteAPIAsync.exceptions.NotFound:
            await ctx.send(f"Failed to find a backpack with the name: {content}.")
            print(f"Failed to find a backpack with the name: {content}.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the emote of the client using the emotes name.",
        help="Sets the emote of the client using the emotes name.\n"
             "Example: !emote Windmill Floss"
    )
    async def emote(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="en",
                searchLang="en",
                matchMethod="contains",
                name=content,
                backendType="AthenaDance"
            )

            await ctx.send(f'Emote set to {cosmetic.id}.')
            print(f"Set emote to: {cosmetic.id}.")
            await self.party.me.clear_emote()
            await self.party.me.set_emote(asset=cosmetic.id)

        except FortniteAPIAsync.exceptions.NotFound:
            await ctx.send(f"Failed to find an emote with the name: {content}.")
            print(f"Failed to find an emote with the name: {content}.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the pickaxe of the client using the pickaxe name.",
        help="Sets the pickaxe of the client using the pickaxe name.\n"
             "Example: !pickaxe Raider's Revenge"
    )
    async def pickaxe(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="en",
                searchLang="en",
                matchMethod="contains",
                name=content,
                backendType="AthenaPickaxe"
            )

            await ctx.send(f'Pickaxe set to {cosmetic.id}.')
            print(f"Set pickaxe to: {cosmetic.id}.")
            await self.party.me.set_pickaxe(asset=cosmetic.id)

        except FortniteAPIAsync.exceptions.NotFound:
            await ctx.send(f"Failed to find a pickaxe with the name: {content}.")
            print(f"Failed to find a pickaxe with the name: {content}.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the pet (backpack) of the client using the pets name.",
        help="Sets the pet (backpack) of the client using the pets name.\n"
             "Example: !pet Bonesy"
    )
    async def pet(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="en",
                searchLang="en",
                matchMethod="contains",
                name=content,
                backendType="AthenaPetCarrier"
            )

            await ctx.send(f'Pet set to {cosmetic.id}.')
            print(f"Set pet to: {cosmetic.id}.")
            await self.party.me.set_pet(asset=cosmetic.id)

        except FortniteAPIAsync.exceptions.NotFound:
            await ctx.send(f"Failed to find a pet with the name: {content}.")
            print(f"Failed to find a pet with the name: {content}.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the emoji of the client using the emojis name.",
        help="Sets the emoji of the client using the emojis name.\n"
             "Example: !emoji Snowball"
    )
    async def emoji(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="en",
                searchLang="en",
                matchMethod="contains",
                name=content,
                backendType="AthenaEmoji"
            )

            await ctx.send(f'Emoji set to {cosmetic.id}.')
            print(f"Set emoji to: {cosmetic.id}.")
            await self.party.me.set_emoji(asset=cosmetic.id)

        except FortniteAPIAsync.exceptions.NotFound:
            await ctx.send(f"Failed to find an emoji with the name: {content}.")
            print(f"Failed to find an emoji with the name: {content}.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the contrail of the client using the contrail name.",
        help="Sets the contrail of the client using the contrail name.\n"
             "Example: !contrail Holly And Divey"
    )
    async def contrail(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="en",
                searchLang="en",
                matchMethod="contains",
                name=content,
                backendType="AthenaSkyDiveContrail"
            )

            await ctx.send(f'Contrail set to {cosmetic.id}.')
            print(f"Set contrail to: {cosmetic.id}.")
            await self.party.me.set_contrail(asset=cosmetic.id)

        except FortniteAPIAsync.exceptions.NotFound:
            await ctx.send(f"Failed to find a contrail with the name: {content}.")
            print(f"Failed to find an contrail with the name: {content}.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client to Purple Skull Trooper.",
        help="Sets the outfit of the client to Purple Skull Trooper.\n"
             "Example: !purpleskull"
    )
    async def purpleskull(self, ctx: fortnitepy.ext.commands.Context) -> None:
        skin_variants = self.party.me.create_variants(
            clothing_color=1
        )

        await self.party.me.set_outfit(
            asset='CID_030_Athena_Commando_M_Halloween',
            variants=skin_variants
        )

        await ctx.send('Skin set to Purple Skull Trooper!')
        print(f"Skin set to Purple Skull Trooper.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client to Pink Ghoul Trooper.",
        help="Sets the outfit of the client to Pink Ghoul Trooper.\n"
             "Example: !pinkghoul"
    )
    async def pinkghoul(self, ctx: fortnitepy.ext.commands.Context) -> None:
        skin_variants = self.party.me.create_variants(
            material=3
        )

        await self.party.me.set_outfit(
            asset='CID_029_Athena_Commando_F_Halloween',
            variants=skin_variants
        )

        await ctx.send('Skin set to Pink Ghoul Trooper!')
        print(f"Skin set to Pink Ghoul Trooper.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the backpack of the client to Purple Ghost Portal.",
        help="Sets the backpack of the client to Purple Ghost Portal.\n"
             "Example: !purpleportal"
    )
    async def purpleportal(self, ctx: fortnitepy.ext.commands.Context) -> None:
        skin_variants = self.party.me.create_variants(
            item='AthenaBackpack',
            particle_config='Particle',
            particle=1
        )

        await self.party.me.set_backpack(
            asset='BID_105_GhostPortal',
            variants=skin_variants
        )

        await ctx.send('Backpack set to Purple Ghost Portal!')
        print(f"Backpack set to Purple Ghost Portal.")

    @commands.dm_only()
    @commands.command(
        description="[Party] Sets the banner of the self.",
        help="Sets the banner of the self.\n"
             "Example: !banner BRSeason01 defaultcolor15 100"
    )
    async def banner(self, ctx: fortnitepy.ext.commands.Context,
                     icon: Optional[str] = None,
                     colour: Optional[str] = None,
                     banner_level: Optional[int] = None
                     ) -> None:
        await self.party.me.set_banner(icon=icon, color=colour, season_level=banner_level)

        await ctx.send(f'Banner set to: {icon} with {colour} at level {banner_level}.')
        print(f"Banner set to: {icon} with {colour} at level {banner_level}.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client using CID.",
        help="Sets the outfit of the client using CID.\n"
             "Example: !cid CID_047_Athena_Commando_F_HolidayReindeer"
    )
    async def cid(self, ctx: fortnitepy.ext.commands.Context, character_id: str) -> None:
        await self.party.me.set_outfit(
            asset=character_id,
            variants=self.party.me.create_variants(profile_banner='ProfileBanner')
        )

        await ctx.send(f'Skin set to {character_id}.')
        print(f'Skin set to {character_id}.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Creates the variants list by the variants you set using VTID.",
        help="Creates the variants list by the variants you set using VTID.\n"
             "Example: !vtid VTID_052_Skull_Trooper_RedFlames"
    )
    async def vtid(self, ctx: fortnitepy.ext.commands.Context, variant_token: str) -> None:
        variant_id = await self.set_vtid(variant_token)

        if variant_id[1].lower() == 'particle':
            skin_variants = self.party.me.create_variants(particle_config='Particle', particle=1)
        else:
            skin_variants = self.party.me.create_variants(**{variant_id[1].lower(): int(variant_id[2])})

        await self.party.me.set_outfit(asset=variant_id[0], variants=skin_variants)
        print(f'Set variants of {variant_id[0]} to {variant_id[1]} {variant_id[2]}.')
        await ctx.send(f'Variants set to {variant_token}.\n'
                       '(Warning: This feature is not supported, please use !variants)')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Creates the variants list by the variants you set.",
        help="Creates the variants list by the variants you set.\n"
             "Example: !variants CID_030_Athena_Commando_M_Halloween clothing_color 1"
    )
    async def variants(self, ctx: fortnitepy.ext.commands.Context, cosmetic_id: str, variant_type: str,
                       variant_int: str) -> None:
        if 'cid' in cosmetic_id.lower() and 'jersey_color' not in variant_type.lower():
            skin_variants = self.party.me.create_variants(
                **{variant_type: int(variant_int) if variant_int.isdigit() else variant_int}
            )

            await self.party.me.set_outfit(
                asset=cosmetic_id,
                variants=skin_variants
            )

        elif 'cid' in cosmetic_id.lower() and 'jersey_color' in variant_type.lower():
            cosmetic_variants = self.party.me.create_variants(
                pattern=0,
                numeric=69,
                **{variant_type: int(variant_int) if variant_int.isdigit() else variant_int}
            )

            await self.party.me.set_outfit(
                asset=cosmetic_id,
                variants=cosmetic_variants
            )

        elif 'bid' in cosmetic_id.lower():
            cosmetic_variants = self.party.me.create_variants(
                item='AthenaBackpack',
                **{variant_type: int(variant_int) if variant_int.isdigit() else variant_int}
            )

            await self.party.me.set_backpack(
                asset=cosmetic_id,
                variants=cosmetic_variants
            )
        elif 'pickaxe_id' in cosmetic_id.lower():
            cosmetic_variants = self.party.me.create_variants(
                item='AthenaPickaxe',
                **{variant_type: int(variant_int) if variant_int.isdigit() else variant_int}
            )

            await self.party.me.set_pickaxe(
                asset=cosmetic_id,
                variants=cosmetic_variants
            )

        await ctx.send(f'Set variants of {cosmetic_id} to {variant_type} {variant_int}.')
        print(f'Set variants of {cosmetic_id} to {variant_type} {variant_int}.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client to Checkered Renegade.",
        help="Sets the outfit of the client to Checkered Renegade.\n"
             "Example: !che"
    )
    async def checkeredrenegade(self, ctx: fortnitepy.ext.commands.Context) -> None:
        skin_variants = self.party.me.create_variants(
            material=2
        )

        await self.party.me.set_outfit(
            asset='CID_028_Athena_Commando_F',
            variants=skin_variants
        )

        await ctx.send('Skin set to Checkered Renegade!')
        print(f'Skin set to Checkered Renegade.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client to Minty Elf.",
        help="Sets the outfit of the client to Minty Elf.\n"
             "Example: !mintyelf"
    )
    async def mintyelf(self, ctx: fortnitepy.ext.commands.Context) -> None:
        skin_variants = self.party.me.create_variants(
            material=2
        )

        await self.party.me.set_outfit(
            asset='CID_051_Athena_Commando_M_HolidayElf',
            variants=skin_variants
        )

        await ctx.send('Skin set to Minty Elf!')
        print(f'Skin set to Minty Elf.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the emote of the client using EID.",
        help="Sets the emote of the client using EID.\n"
             "Example: !eid EID_Floss"
    )
    async def eid(self, ctx: fortnitepy.ext.commands.Context, emote_id: str) -> None:
        await self.party.me.clear_emote()
        await self.party.me.set_emote(
            asset=emote_id
        )

        await ctx.send(f'Emote set to {emote_id}!')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Clears/stops the emote currently playing.",
        help="Clears/stops the emote currently playing.\n"
             "Example: !stop"
    )
    async def stop(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.clear_emote()
        await ctx.send('Stopped emoting.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the backpack of the client using BID.",
        help="Sets the backpack of the client using BID.\n"
             "Example: !bid BID_023_Pinkbear"
    )
    async def bid(self, ctx: fortnitepy.ext.commands.Context, backpack_id: str) -> None:
        await self.party.me.set_backpack(
            asset=backpack_id
        )

        await ctx.send(f'Backbling set to {backpack_id}!')

    @commands.dm_only()
    @commands.command(
        aliases=['legacypickaxe'],
        description="[Cosmetic] Sets the pickaxe of the client using PICKAXE_ID",
        help="Sets the pickaxe of the client using PICKAXE_ID\n"
             "Example: !pickaxe_id Pickaxe_ID_073_Balloon"
    )
    async def pickaxe_id(self, ctx: fortnitepy.ext.commands.Context, pickaxe_id_: str) -> None:
        await self.party.me.set_pickaxe(
            asset=pickaxe_id_
        )

        await ctx.send(f'Pickaxe set to {pickaxe_id_}')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the pet of the client using PetCarrier_.",
        help="Sets the pet of the client using PetCarrier_.\n"
             "Example: !pet_carrier PetCarrier_002_Chameleon"
    )
    async def pet_carrier(self, ctx: fortnitepy.ext.commands.Context, pet_carrier_id: str) -> None:
        await self.party.me.set_pet(
            asset=pet_carrier_id
        )

        await ctx.send(f'Pet set to {pet_carrier_id}!')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the emoji of the client using Emoji_.",
        help="Sets the emoji of the client using Emoji_.\n"
             "Example: !emoji_id Emoji_PeaceSign"
    )
    async def emoji_id(self, ctx: fortnitepy.ext.commands.Context, emoji_: str) -> None:
        await self.party.me.clear_emote()
        await self.party.me.set_emoji(
            asset=emoji_
        )

        await ctx.send(f'Emoji set to {emoji_}!')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the contrail of the client using Trails_.",
        help="Sets the contrail of the client using Trails_.\n"
             "Example: !trails Trails_ID_075_Celestial"
    )
    async def trails(self, ctx: fortnitepy.ext.commands.Context, trails_: str) -> None:
        await self.party.me.set_contrail(
            asset=trails_
        )

        await ctx.send(f'Contrail set to {trails_}!')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets pickaxe using PICKAXE_ID or display name & does 'Point it Out'. If no pickaxe is "
                    "specified, only the emote will be played.",
        help="Sets pickaxe using PICKAXE_ID or display name & does 'Point it Out'. If no pickaxe is "
             "specified, only the emote will be played.\n"
             "Example: !point Pickaxe_ID_029_Assassin"
    )
    async def point(self, ctx: fortnitepy.ext.commands.Context, *, content: Optional[str] = None) -> None:
        if content is None:
            await self.party.me.set_emote(asset='EID_IceKing')
            await ctx.send(f'Point it Out played.')
        elif 'pickaxe_id' in content.lower():
            await self.party.me.set_pickaxe(asset=content)
            await self.party.me.set_emote(asset='EID_IceKing')
            await ctx.send(f'Pickaxe set to {content} & Point it Out played.')
        else:
            try:
                cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                    lang="en",
                    searchLang="en",
                    matchMethod="contains",
                    name=content,
                    backendType="AthenaPickaxe"
                )

                await self.party.me.set_pickaxe(asset=cosmetic.id)
                await self.party.me.clear_emote()
                await self.party.me.set_emote(asset='EID_IceKing')
                await ctx.send(f'Pickaxe set to {content} & Point it Out played.')
            except FortniteAPIAsync.exceptions.NotFound:
                await ctx.send(f"Failed to find a pickaxe with the name: {content}")

    @commands.dm_only()
    @commands.command(
        description="[Party] Sets the readiness of the client to ready.",
        help="Sets the readiness of the client to ready.\n"
             "Example: !ready"
    )
    async def ready(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_ready(fortnitepy.ReadyState.READY)
        await ctx.send('Ready!')

    @commands.dm_only()
    @commands.command(
        aliases=['sitin'],
        description="[Party] Sets the readiness of the client to unready.",
        help="Sets the readiness of the client to unready.\n"
             "Example: !unready"
    )
    async def unready(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
        await ctx.send('Unready!')

    @commands.dm_only()
    @commands.command(
        description="[Party] Sets the readiness of the client to SittingOut.",
        help="Sets the readiness of the client to SittingOut.\n"
             "Example: !sitout"
    )
    async def sitout(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
        await ctx.send('Sitting Out!')

    @commands.dm_only()
    @commands.command(
        description="[Party] Sets the battlepass info of the self.",
        help="Sets the battlepass info of the self.\n"
             "Example: !bp 100"
    )
    async def bp(self, ctx: fortnitepy.ext.commands.Context, tier: int) -> None:
        await self.party.me.set_battlepass_info(
            has_purchased=True,
            level=tier,
        )

        await ctx.send(f'Set battle pass tier to {tier}.')

    @commands.dm_only()
    @commands.command(
        description="[Party] Sets the level of the self.",
        help="Sets the level of the self.\n"
             "Example: !level 999"
    )
    async def level(self, ctx: fortnitepy.ext.commands.Context, banner_level: int) -> None:
        await self.party.me.set_banner(
            season_level=banner_level
        )

        await ctx.send(f'Set level to {banner_level}.')

    @commands.dm_only()
    @commands.command(
        description="[Party] Sends message to party chat with the given content.",
        help="Sends message to party chat with the given content.\n"
             "Example: !echo i cant fix the fucking public lobby bots"
    )
    async def echo(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        await self.party.send(content)
        await ctx.send('Sent message to party chat.')

    @commands.dm_only()
    @commands.command(
        description="[Client] Sends and sets the status.",
        help="Sends and sets the status.\n"
             "Example: !status Presence Unknown"
    )
    async def status(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        await self.set_presence(content)

        await ctx.send(f'Status set to {content}')
        print(f'Status set to {content}.')

    @commands.dm_only()
    @commands.command(
        description="[Party] Leaves the current party.",
        help="Leaves the current party.\n"
             "Example: !leave"
    )
    async def leave(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_emote('EID_Wave')
        await self.party.me.leave()
        await ctx.send('Bye!')

        print(f'Left the party as I was requested.')

    @commands.dm_only()
    @commands.command(
        description="[Party] Kicks the inputted user.",
        help="Kicks the inputted user.\n"
             "Example: !kick Cxnyaa"
    )
    async def kick(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: str) -> None:
        user = await self.fetch_user(epic_username)
        member = self.party.members.get(user.id)

        if member is None:
            await ctx.send("Failed to find that user, are you sure they're in the party?")
        else:
            try:
                await member.kick()
                await ctx.send(f"Kicked user: {member.display_name}.")
                print(f"Kicked user: {member.display_name}")
            except fortnitepy.errors.Forbidden:
                await ctx.send(f"Failed to kick {member.display_name}, as I'm not party leader.")
                print(crayons.red(f"[ERROR] "
                                  "Failed to kick member as I don't have the required permissions."))

    @commands.dm_only()
    @commands.command(
        aliases=['unhide'],
        description="[Party] Promotes the defined user to party leader. If friend is left blank, "
                    "the message author will be used.",
        help="Promotes the defined user to party leader. If friend is left blank, the message author will be used.\n"
             "Example: !promote mxnty"
    )
    async def promote(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            user = await self.fetch_user(ctx.author.display_name)
            member = self.party.members.get(user.id)
        else:
            user = await self.fetch_user(epic_username)
            member = self.party.members.get(user.id)

        if member is None:
            await ctx.send("Failed to find that user, are you sure they're in the party?")
        else:
            try:
                await member.promote()
                await ctx.send(f"Promoted user: {member.display_name}.")
                print(f"Promoted user: {member.display_name}")
            except fortnitepy.errors.Forbidden:
                await ctx.send(f"Failed topromote {member.display_name}, as I'm not party leader.")
                print(crayons.red(f"[ERROR] "
                                  "Failed to kick member as I don't have the required permissions."))

    @commands.dm_only()
    @commands.command(
        description="[Party] Sets the lobbies selected playlist.",
        help="Sets the lobbies selected playlist.\n"
             "Example: !playlist_id Playlist_Tank_Solo"
    )
    async def playlist_id(self, ctx: fortnitepy.ext.commands.Context, playlist_: str) -> None:
        try:
            await self.party.set_playlist(playlist=playlist_)
            await ctx.send(f'Gamemode set to {playlist_}')
        except fortnitepy.errors.Forbidden:
            await ctx.send(f"Failed to set gamemode to {playlist_}, as I'm not party leader.")
            print(crayons.red(f"[ERROR] "
                              "Failed to set gamemode as I don't have the required permissions."))

    @commands.dm_only()
    @commands.command(
        description="[Party] Sets the parties current privacy.",
        help="Sets the parties current privacy.\n"
             "Example: !privacy private"
    )
    async def privacy(self, ctx: fortnitepy.ext.commands.Context, privacy_type: str) -> None:
        try:
            if privacy_type.lower() == 'public':
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            elif privacy_type.lower() == 'private':
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PRIVATE)
            elif privacy_type.lower() == 'friends':
                await self.party.set_privacy(fortnitepy.PartyPrivacy.FRIENDS)
            elif privacy_type.lower() == 'friends_allow_friends_of_friends':
                await self.party.set_privacy(fortnitepy.PartyPrivacy.FRIENDS_ALLOW_FRIENDS_OF_FRIENDS)
            elif privacy_type.lower() == 'private_allow_friends_of_friends':
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PRIVATE_ALLOW_FRIENDS_OF_FRIENDS)

            await ctx.send(f'Party privacy set to {self.party.privacy}.')
            print(f'Party privacy set to {self.party.privacy}.')

        except fortnitepy.errors.Forbidden:
            await ctx.send(f"Failed to set party privacy to {privacy_type}, as I'm not party leader.")
            print(crayons.red(f"[ERROR] "
                              "Failed to set party privacy as I don't have the required permissions."))

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Copies the cosmetic loadout of the defined user. If user is left blank, "
                    "the message author will be used.",
        help="Copies the cosmetic loadout of the defined user. If user is left blank, the message author will be used."
             "\nExample: !copy Terbau"
    )
    async def copy(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            member = self.party.members.get(ctx.author.id)
        else:
            user = await self.fetch_user(epic_username)
            member = self.party.members.get(user.id)

        await self.party.me.edit(
            functools.partial(
                fortnitepy.ClientPartyMember.set_outfit,
                asset=member.outfit,
                variants=member.outfit_variants
            ),
            functools.partial(
                fortnitepy.ClientPartyMember.set_backpack,
                asset=member.backpack,
                variants=member.backpack_variants
            ),
            functools.partial(
                fortnitepy.ClientPartyMember.set_pickaxe,
                asset=member.pickaxe,
                variants=member.pickaxe_variants
            ),
            functools.partial(
                fortnitepy.ClientPartyMember.set_banner,
                icon=member.banner[0],
                color=member.banner[1],
                season_level=member.banner[2]
            ),
            functools.partial(
                fortnitepy.ClientPartyMember.set_battlepass_info,
                has_purchased=True,
                level=member.battlepass_info[1]
            )
        )

        await self.party.me.set_emote(asset=member.emote)
        await ctx.send(f'Copied the loadout of {member.display_name}.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Shortcut for equipping the skin CID_VIP_Athena_Commando_M_GalileoGondola_SG.",
        help="Shortcut for equipping the skin CID_VIP_Athena_Commando_M_GalileoGondola_SG.\n"
             "Example: !hologram"
    )
    async def hologram(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(
            asset='CID_VIP_Athena_Commando_M_GalileoGondola_SG'
        )

        await ctx.send('Skin set to Star Wars Hologram!')
        print(f'Skin set to Star Wars Hologram.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Shortcut for equipping the skin CID_VIP_Athena_Commando_M_GalileoGondola_SG.",
        help="Shortcut for equipping the skin CID_VIP_Athena_Commando_M_GalileoGondola_SG.\n"
             "Example: !gift is a joke command."
    )
    async def gift(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.clear_emote()

        await self.party.me.set_emote(
            asset='EID_NeverGonna'
        )

        await ctx.send('What did you think would happen?')

    @commands.dm_only()
    @commands.command(
        description="[Party] Sets the parties custom matchmaking code.",
        help="Sets the parties custom matchmaking code.\n"
             "Example: !skin Nog Ops"
    )
    async def matchmakingcode(self, ctx: fortnitepy.ext.commands.Context, *, custom_matchmaking_key: str) -> None:
        await self.party.set_custom_key(
            key=custom_matchmaking_key
        )

        await ctx.send(f'Custom matchmaking code set to: {custom_matchmaking_key}')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Shortcut for equipping the emote EID_TourBus.",
        help="Shortcut for equipping the emote EID_TourBus.\n"
             "Example: !ponpon"
    )
    async def ponpon(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_emote(
            asset='EID_TourBus'
        )

        await ctx.send('Emote set to Ninja Style!')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the enlightened value of a skin "
                    "(used for skins such as glitched Scratch or Golden Peely).",
        help="Sets the enlightened value of a skin.\n"
             "Example: !enlightened CID_701_Athena_Commando_M_BananaAgent 2 350"
    )
    async def enlightened(self, ctx: fortnitepy.ext.commands.Context, cosmetic_id: str, br_season: int,
                          skin_level: int) -> None:
        variant_types = {
            1: self.party.me.create_variants(progressive=4),
            2: self.party.me.create_variants(progressive=4),
            3: self.party.me.create_variants(material=2)
        }

        if 'cid' in cosmetic_id.lower():
            await self.party.me.set_outfit(
                asset=cosmetic_id,
                variants=variant_types[br_season] if br_season in variant_types else variant_types[2],
                enlightenment=(br_season, skin_level)
            )

            await ctx.send(f'Skin set to {cosmetic_id} at level {skin_level} (for Season 1{br_season}).')
        elif 'bid' in cosmetic_id.lower():
            await self.party.me.set_backpack(
                asset=cosmetic_id,
                variants=self.party.me.create_variants(progressive=2),
                enlightenment=(br_season, skin_level)
            )
            await ctx.send(f'Backpack set to {cosmetic_id} at level {skin_level} (for Season 1{br_season}).')

        print(f'Enlightenment for {cosmetic_id} '
              f'set to level {skin_level} (for Season 1{br_season}).')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Shortcut for equipping the skin CID_605_Athena_Commando_M_TourBus.",
        help="Shortcut for equipping the skin CID_605_Athena_Commando_M_TourBus.\n"
             "Example: !ninja"
    )
    async def ninja(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(
            asset='CID_605_Athena_Commando_M_TourBus'
        )

        await ctx.send('Skin set to Ninja!')
        print(f'Skin set to Ninja.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Equips all very rare skins.",
        help="Equips all very rare skins.\n"
             "Example: !rareskins"
    )
    async def rareskins(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await ctx.send('Showing all rare skins now.')

        await self.party.me.set_outfit(
            asset='CID_030_Athena_Commando_M_Halloween',
            variants=self.party.me.create_variants(clothing_color=1)
        )

        await ctx.send('Skin set to Purple Skull Trooper!')
        print(f"Skin set to Purple Skull Trooper.")

        await self.party.me.set_outfit(
            asset='CID_029_Athena_Commando_F_Halloween',
            variants=self.party.me.create_variants(material=3)
        )

        await ctx.send('Skin set to Pink Ghoul Trooper!')
        print(f"Skin set to Pink Ghoul Trooper.")

        for rare_skin in ('CID_028_Athena_Commando_F', 'CID_017_Athena_Commando_M'):
            await self.party.me.set_outfit(
                asset=rare_skin
            )

            await ctx.send(f'Skin set to {rare_skin}!')
            print(f"Skin set to: {rare_skin}!")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client to Golden Peely "
                    "(shortcut for !enlightened CID_701_Athena_Commando_M_BananaAgent 2 350).",
        help="Sets the outfit of the client to Golden Peely.\n"
             "Example: !goldenpeely"
    )
    async def goldenpeely(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(
            asset='CID_701_Athena_Commando_M_BananaAgent',
            variants=self.party.me.create_variants(progressive=4),
            enlightenment=(2, 350)
        )

        await ctx.send(f'Skin set to Golden Peely.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Randomly finds & equips a skin. Types currently include skin, backpack, emote & all. "
                    "If type is left blank, a random skin will be equipped.",
        help="Randomly finds & equips a skin.\n"
             "Example: !random skin"
    )
    async def random(self, ctx: fortnitepy.ext.commands.Context, cosmetic_type: str = 'skin') -> None:
        if cosmetic_type == 'skin':
            all_outfits = await self.fortnite_api.cosmetics.get_cosmetics(
                lang="en",
                searchLang="en",
                backendType="AthenaCharacter"
            )

            random_skin = py_random.choice(all_outfits)

            await self.party.me.set_outfit(
                asset=random_skin.id,
                variants=self.party.me.create_variants(profile_banner='ProfileBanner')
            )

            await ctx.send(f'Skin randomly set to {random_skin.name}.')
            print(f'Skin randomly set to {random_skin.name}.')

        elif cosmetic_type == 'backpack':
            all_backpacks = await self.fortnite_api.cosmetics.get_cosmetics(
                lang="en",
                searchLang="en",
                backendType="AthenaBackpack"
            )

            random_backpack = py_random.choice(all_backpacks)

            await self.party.me.set_backpack(
                asset=random_backpack.id,
                variants=self.party.me.create_variants(profile_banner='ProfileBanner')
            )

            await ctx.send(f'Backpack randomly set to {random_backpack.name}.')
            print(f'Backpack randomly set to {random_backpack.name}.')

        elif cosmetic_type == 'emote':
            all_emotes = await self.fortnite_api.cosmetics.get_cosmetics(
                lang="en",
                searchLang="en",
                backendType="AthenaDance"
            )

            random_emote = py_random.choice(all_emotes)

            await self.party.me.set_emote(
                asset=random_emote.id
            )

            await ctx.send(f'Emote randomly set to {random_emote.name}.')
            print(f'Emote randomly set to {random_emote.name}.')

        elif cosmetic_type == 'all':
            all_outfits = await self.fortnite_api.cosmetics.get_cosmetics(
                lang="en",
                searchLang="en",
                backendType="AthenaCharacter"
            )

            all_backpacks = await self.fortnite_api.cosmetics.get_cosmetics(
                lang="en",
                searchLang="en",
                backendType="AthenaBackpack"
            )

            all_emotes = await self.fortnite_api.cosmetics.get_cosmetics(
                lang="en",
                searchLang="en",
                backendType="AthenaDance"
            )

            random_outfit = py_random.choice(all_outfits).id
            random_backpack = py_random.choice(all_backpacks).id
            random_emote = py_random.choice(all_emotes).id

            await self.party.me.set_outfit(
                asset=random_outfit
            )

            await ctx.send(f'Skin randomly set to {random_outfit}.')

            await self.party.me.set_backpack(
                asset=random_backpack
            )

            await ctx.send(f'Backpack randomly set to {random_backpack}.')

            await self.party.me.set_emote(
                asset=random_emote
            )

            await ctx.send(f'Emote randomly set to {random_emote}.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Clears the currently set backpack.",
        help="Clears the currently set backpack.\n"
             "Example: !nobackpack"
    )
    async def nobackpack(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.clear_backpack()
        await ctx.send('Removed backpack.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Clears the currently set pet.",
        help="Clears the currently set pet.\n"
             "Example: !nopet"
    )
    async def nopet(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.clear_pet()
        await ctx.send('Removed pet.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Clears the currently set contrail.",
        help="Clears the currently set contrail.\n"
             "Example: !nocontrail"
    )
    async def nocontrail(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.clear_contrail()
        await ctx.send('Removed contrail.')

    @commands.dm_only()
    @commands.command(
        description="[Party] Sets the client to the \"In Match\" state. If the first argument is 'progressive', "
                    "the players remaining will gradually drop to mimic a real game.",
        help="Sets the client to the \"In Match\" state.\n"
             "Example: !match 69 420"
    )
    async def match(self,
                    ctx: fortnitepy.ext.commands.Context,
                    players: Union[str, int] = 0,
                    match_time: int = 0) -> None:
        if players == 'progressive':
            match_time = datetime.datetime.utcnow()

            await self.party.me.set_in_match(
                players_left=100,
                started_at=match_time
            )

            while (100 >= self.party.me.match_players_left > 0
                   and self.party.me.in_match()):
                await self.party.me.set_in_match(
                    players_left=self.party.me.match_players_left - py_random.randint(3, 6),
                    started_at=match_time
                )

        else:
            await self.party.me.set_in_match(
                players_left=int(players),
                started_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=match_time)
            )

            await ctx.send(f'Set state to in-game in a match with {players} players.'
                           '\nUse the command: !lobby to revert back to normal.')

    @commands.dm_only()
    @commands.command(
        description="[Party] Sets the client to normal pre-game lobby state.",
        help="Sets the client to normal pre-game lobby state.\n"
             "Example: !lobby"
    )
    async def lobby(self, ctx: fortnitepy.ext.commands.Context) -> None:
        if self.default_party_member_config.cls == fortnitepy.JustChattingClientPartyMember:
            self.default_party_member_config.cls = fortnitepy.ClientPartyMember

            party_id = self.party.id
            await self.party.me.leave()

            await ctx.send('Removed state of Just Chattin\'. Now attempting to rejoin party.')

            try:
                await self.join_party(party_id)
            except fortnitepy.errors.Forbidden:
                await ctx.send('Failed to join back as party is set to private.')
            except fortnitepy.errors.NotFound:
                await ctx.send('Party not found, are you sure Fortnite is open?')

        await self.party.me.clear_in_match()

        await ctx.send('Set state to the pre-game lobby.')

    @commands.dm_only()
    @commands.command(
        description="[Party] Joins the party of the defined friend. If friend is left blank, "
                    "the message author will be used.",
        help="Joins the party of the defined friend.\n"
             "Example: !join Terbau"
    )
    async def join(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            epic_friend = self.get_friend(ctx.author.id)
        else:
            user = await self.fetch_user(epic_username)

            if user is not None:
                epic_friend = self.get_friend(user.id)
            else:
                epic_friend = None
                await ctx.send(f'Failed to find user with the name: {epic_username}.')

        if isinstance(epic_friend, fortnitepy.Friend):
            try:
                await epic_friend.join_party()
                await ctx.send(f'Joined the party of {epic_friend.display_name}.')
            except fortnitepy.errors.Forbidden:
                await ctx.send('Failed to join party since it is private.')
            except fortnitepy.errors.PartyError:
                await ctx.send('Party not found, are you sure Fortnite is open?')
        else:
            await ctx.send('Cannot join party as the friend is not found.')

    @commands.dm_only()
    @commands.command(
        description="[Party] Sends the defined user a friend request.",
        help="Sends the defined user a friend request.\n"
             "Example: !friend Ninja"
    )
    async def friend(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: str) -> None:
        user = await self.fetch_user(epic_username)

        if user is not None:
            await self.add_friend(user.id)
            await ctx.send(f'Sent/accepted friend request to/from {user.display_name}.')
            print(f'Sent/accepted friend request to/from {user.display_name}.')
        else:
            await ctx.send(f'Failed to find user with the name: {epic_username}.')
            print(
                crayons.red(f"[ERROR] Failed to find a user with the name {epic_username}."))

    @commands.dm_only()
    @commands.command(
        description="[Party] Sets the lobbies selected playlist using playlist name.",
        help="Sets the lobbies selected playlist using playlist name.\n"
             "Example: !playlist Food Fight"
    )
    async def playlist(self, ctx: fortnitepy.ext.commands.Context, *, playlist_name: str) -> None:
        try:
            scuffedapi_playlist_id = await self.fortnite_api.get_playlist(playlist_name)

            if scuffedapi_playlist_id is not None:
                await self.party.set_playlist(playlist=scuffedapi_playlist_id)
                await ctx.send(f'Playlist set to {scuffedapi_playlist_id}.')
                print(f'Playlist set to {scuffedapi_playlist_id}.')

            else:
                await ctx.send(f'Failed to find a playlist with the name: {playlist_name}.')
                print(crayons.red(f"[ERROR] "
                                  f"Failed to find a playlist with the name: {playlist_name}."))

        except fortnitepy.errors.Forbidden:
            await ctx.send(f"Failed to set playlist to {playlist_name}, as I'm not party leader.")
            print(crayons.red(f"[ERROR] "
                              "Failed to set playlist as I don't have the required permissions."))

    @commands.dm_only()
    @commands.command(
        name="invite",
        description="[Party] Invites the defined friend to the party. If friend is left blank, "
                    "the message author will be used.",
        help="Invites the defined friend to the party.\n"
             "Example: !invite Terbau"
    )
    async def _invite(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            epic_friend = self.get_friend(ctx.author.id)
        else:
            user = await self.fetch_user(epic_username)

            if user is not None:
                epic_friend = self.get_friend(user.id)
            else:
                epic_friend = None
                await ctx.send(f'Failed to find user with the name: {epic_username}.')
                print(crayons.red(f"[ERROR] "
                                  f"Failed to find user with the name: {epic_username}."))

        if isinstance(epic_friend, fortnitepy.Friend):
            try:
                await epic_friend.invite()
                await ctx.send(f'Invited {epic_friend.display_name} to the party.')
                print(f"[ERROR] Invited {epic_friend.display_name} to the party.")
            except fortnitepy.errors.PartyError:
                await ctx.send('Failed to invite friend as they are either already in the party or it is full.')
                print(crayons.red(f"[ERROR] "
                                  "Failed to invite to party as friend is already either in party or it is full."))
        else:
            await ctx.send('Cannot invite to party as the friend is not found.')
            print(crayons.red(f"[ERROR] "
                              "Failed to invite to party as the friend is not found."))

    @commands.dm_only()
    @commands.command(
        description="[Party] Hides everyone in the party except for the bot but if a player is specified, "
                    "that specific player will be hidden.",
        help="Hides members of the party.\n"
             "Example: !hide"
    )
    async def hide(self, ctx: fortnitepy.ext.commands.Context, party_member: Optional[str] = None) -> None:
        if self.party.me.leader:
            if party_member is not None:
                user = await self.fetch_user(party_member)
                member = self.party.members.get(user.id)

                if member is not None:
                    raw_squad_assignments = self.party.meta.get_prop(
                        'Default:RawSquadAssignments_j'
                    )["RawSquadAssignments"]

                    for player in raw_squad_assignments:
                        if player['memberId'] == member.id:
                            raw_squad_assignments.remove(player)

                    await self.party.set_and_update_party_prop(
                        'Default:RawSquadAssignments_j', {
                            'RawSquadAssignments': raw_squad_assignments
                        }
                    )
                else:
                    await ctx.send(f'Failed to find user with the name: {party_member}.')
                    print(crayons.red(f"[ERROR] "
                                      f"Failed to find user with the name: {party_member}."))
            else:
                await self.party.set_and_update_party_prop(
                    'Default:RawSquadAssignments_j', {
                        'RawSquadAssignments': [{'memberId': self.user.id, 'absoluteMemberIdx': 1}]
                    }
                )

                await ctx.send('Hid everyone in the party. Use !unhide if you want to unhide everyone.'
                               '\nReminder: Crashing lobbies is bannable offense which will result in a permanent ban.')
                print(f'Hid everyone in the party.')
        else:
            await ctx.send("Failed to hide everyone, as I'm not party leader")
            print(crayons.red(f"[ERROR] "
                              "Failed to hide everyone as I don't have the required permissions."))

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client using the outfits name with the ghost variant.",
        help="Sets the outfit of the client using the outfits name with the ghost variant.\n"
             "Example: !ghost Meowscles"
    )
    async def ghost(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            skin_variants = self.party.me.create_variants(
                progressive=2
            )

            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="en",
                searchLang="en",
                matchMethod="contains",
                name=content,
                backendType="AthenaCharacter"
            )

            await self.party.me.set_outfit(
                asset=cosmetic.id,
                variants=skin_variants
            )

            await ctx.send(f'Skin set to Ghost {cosmetic.name}!')
            print(f'Skin set to Ghost {cosmetic.name}.')

        except FortniteAPIAsync.exceptions.NotFound:
            await ctx.send(f"Failed to find a skin with the name: {content}.")
            print(f"Failed to find a skin with the name: {content}.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client using the outfits name with the shadow variant.",
        help="Sets the outfit of the client using the outfits name with the shadow variant.\n"
             "Example: !shadow Midas"
    )
    async def shadow(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            skin_variants = self.party.me.create_variants(
                progressive=3
            )

            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="en",
                searchLang="en",
                matchMethod="contains",
                name=content,
                backendType="AthenaCharacter"
            )

            await self.party.me.set_outfit(
                asset=cosmetic.id,
                variants=skin_variants
            )

            await ctx.send(f'Skin set to Shadow {cosmetic.name}!')
            print(f'Skin set to Ghost {cosmetic.name}.')

        except FortniteAPIAsync.exceptions.NotFound:
            await ctx.send(f"Failed to find a skin with the name: {content}.")
            print(f"Failed to find a skin with the name: {content}.")

    @commands.dm_only()
    @commands.command(
        description="[Client] Sets the clients kairos/PartyHub avatar.",
        help="Sets the clients kairos/PartyHub avatar.\n"
             "Example: !avatar stw_soldier_f"
    )
    async def avatar(self, ctx: fortnitepy.ext.commands.Context, kairos_cid: str) -> None:
        kairos_avatar = fortnitepy.Avatar(
            asset=kairos_cid
        )

        self.set_avatar(kairos_avatar)

        await ctx.send(f'Kairos avatar set to {kairos_cid}.')
        print(f'Kairos avatar set to {kairos_cid}.')

    @commands.dm_only()
    @commands.command(
        aliases=['clear'],
        description="[Client] Clears command prompt/terminal.",
        help="Clears command prompt/terminal.\n"
             "Example: !clean"
    )
    async def clean(self, ctx: fortnitepy.ext.commands.Context) -> None:
        os.system('cls' if 'win' in sys.platform else 'clear')

        print(crayons.cyan(f'Silverbot Made By mxnty.'))
        print(crayons.cyan(
            f'Discord server: https://discord.gg/7cn33ZhZBg - For support, questions, etc.'))

        await ctx.send('Command prompt/terminal cleared.')
        print(f'Command prompt/terminal cleared.')

    @commands.dm_only()
    @commands.command(
        name="set",
        description="[Cosmetic] Equips all cosmetics from a set.",
        help="Equips all cosmetics from a set.\n"
             "Example: !set Fort Knights"
    )
    async def _set(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        cosmetic_types = {
            "AthenaBackpack": self.party.me.set_backpack,
            "AthenaCharacter": self.party.me.set_outfit,
            "AthenaEmoji": self.party.me.set_emoji,
            "AthenaDance": self.party.me.set_emote
        }

        set_items = await self.fortnite_api.cosmetics.get_cosmetics(
            lang="en",
            searchLang="en",
            matchMethod="contains",
            set=content
        )

        await ctx.send(f'Equipping all cosmetics from the {set_items[0].set} set.')
        print(f'Equipping all cosmetics from the {set_items[0].set} set.')

        for cosmetic in set_items:
            if cosmetic.backend_type.value in cosmetic_types:
                await cosmetic_types[cosmetic.backend_type.value](asset=cosmetic.id)

                await ctx.send(f'{cosmetic.short_description} set to {cosmetic.name}!')
                print(f'{cosmetic.short_description} set to {cosmetic.name}.')


        await ctx.send(f'Finished equipping all cosmetics from the {set_items[0].set} set.')
        print(f'Fishing equipping  all cosmetics from the {set_items[0].set} set.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Creates the variants list by the variants you set from skin name. "
                    "If you want to include spaces in the skin name, you need to enclose it in \"'s.",
        help="Creates the variants list by the variants you set from skin name.\n"
             "Example: !style \"Skull Trooper\" clothing_color 1"
    )
    async def style(self, ctx: fortnitepy.ext.commands.Context, cosmetic_name: str, variant_type: str,
                    variant_int: str) -> None:
        # cosmetic_types = {
        #     "AthenaCharacter": self.party.me.set_outfit,
        #     "AthenaBackpack": self.party.me.set_backpack,
        #     "AthenaPickaxe": self.party.me.set_pickaxe
        # }

        cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
            lang="en",
            searchLang="en",
            matchMethod="contains",
            name=cosmetic_name,
            backendType="AthenaCharacter"
        )

        cosmetic_variants = self.party.me.create_variants(
            # item=cosmetic.backend_type.value,
            **{variant_type: int(variant_int) if variant_int.isdigit() else variant_int}
        )

        # await cosmetic_types[cosmetic.backend_type.value](
        await self.party.me.set_outfit(
            asset=cosmetic.id,
            variants=cosmetic_variants
        )

        await ctx.send(f'Set variants of {cosmetic.id} to {variant_type} {variant_int}.')
        print(f'Set variants of {cosmetic.id} to {variant_type} {variant_int}.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Equips all new non encrypted skins.",
        help="Equips all new non encrypted skins.\n"
             "Example: !new"
    )
    async def new(self, ctx: fortnitepy.ext.commands.Context) -> None:
        new_skins = await self.fortnite_api.cosmetics.get_new_cosmetics()

        for new_skin in [new_cid for new_cid in new_skins if new_cid.split('/')[-1].lower().startswith('cid_')]:
            await self.party.me.set_outfit(
                asset=new_skin.split('/')[-1].split('.uasset')[0]
            )

            await ctx.send(f"Skin set to {new_skin.split('/')[-1].split('.uasset')[0]}!")
            print(f"Skin set to: {new_skin.split('/')[-1].split('.uasset')[0]}!")


        await ctx.send(f'Finished equipping all new unencrypted skins.')
        print(f'Finished equipping all new unencrypted skins.')

        for new_emote in [new_eid for new_eid in new_skins if new_eid.split('/')[-1].lower().startswith('eid_')]:
            await self.party.me.set_emote(
                asset=new_emote.split('/')[-1].split('.uasset')[0]
            )

            await ctx.send(f"Emote set to {new_emote.split('/')[-1].split('.uasset')[0]}!")
            print(f"Emote set to: {new_emote.split('/')[-1].split('.uasset')[0]}!")


        await ctx.send(f'Finished equipping all new unencrypted skins.')
        print(f'Finished equipping all new unencrypted skins.')

    @commands.dm_only()
    @commands.command(
        description="[Party] Sets the client to the \"Just Chattin'\" state.",
        help="Sets the client to the \"Just Chattin'\" state.\n"
             "Example: !justchattin"
    )
    async def justchattin(self, ctx: fortnitepy.ext.commands.Context) -> None:
        self.default_party_member_config.cls = fortnitepy.JustChattingClientPartyMember

        party_id = self.party.id
        await self.party.me.leave()

        await ctx.send('Set state to Just Chattin\'. Now attempting to rejoin party.'
                       '\nUse the command: !lobby to revert back to normal.')

        try:
            await self.join_party(party_id)
        except fortnitepy.errors.Forbidden:
            await ctx.send('Failed to join back as party is set to private.')
        except fortnitepy.errors.NotFound:
            await ctx.send('Party not found, are you sure Fortnite is open?')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Equips all skins currently in the item shop.",
        help="Equips all skins currently in the item shop.\n"
             "Example: !shop"
    )
    async def shop(self, ctx: fortnitepy.ext.commands.Context) -> None:
        store = await self.fetch_item_shop()

        await ctx.send(f"Equipping all skins in today's item shop.")
        print(f"Equipping all skins in today's item shop.")

        for item in store.special_featured_items + \
                store.special_daily_items + \
                store.special_featured_items + \
                store.special_daily_items:
            for grant in item.grants:
                if grant['type'] == 'AthenaCharacter':
                    await self.party.me.set_outfit(
                        asset=grant['asset']
                    )

                    await ctx.send(f"Skin set to {item.display_names[0]}!")
                    print(f"Skin set to: {item.display_names[0]}!")


        await ctx.send(f'Finished equipping all skins in the item shop.')
        print(f'Finished equipping all skins in the item shop.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Equips a random old default skin.",
        help="Equips a random old default skin.\n"
             "Example: !olddefault"
    )
    async def olddefault(self, ctx: fortnitepy.ext.commands.Context) -> None:
        random_default = py_random.choice(
            [cid_ for cid_ in dir(fortnitepy.DefaultCharactersChapter1) if not cid_.startswith('_')]
        )

        await self.party.me.set_outfit(
            asset=random_default
        )

        await ctx.send(f'Skin set to {random_default}!')
        print(f"Skin set to {random_default}.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client to Hatless Recon Expert.",
        help="Sets the outfit of the client to Hatless Recon Expert.\n"
             "Example: !hatlessrecon"
    )
    async def hatlessrecon(self, ctx: fortnitepy.ext.commands.Context) -> None:
        skin_variants = self.party.me.create_variants(
            parts=2
        )

        await self.party.me.set_outfit(
            asset='CID_022_Athena_Commando_F',
            variants=skin_variants
        )

        await ctx.send('Skin set to Hatless Recon Expert!')
        print(f'Skin set to Hatless Recon Expert.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the to the max tier skin in the defined season.",
        help="Sets the outfit of the to the max tier skin in the defined season.\n"
             "Example: !season 2"
    )
    async def season(self, ctx: fortnitepy.ext.commands.Context, br_season: int) -> None:
        max_tier_skins = {
            1: "CID_028_Athena_Commando_F",
            2: "CID_035_Athena_Commando_M_Medieval",
            3: "CID_084_Athena_Commando_M_Assassin",
            4: "CID_116_Athena_Commando_M_CarbideBlack",
            5: "CID_165_Athena_Commando_M_DarkViking",
            6: "CID_230_Athena_Commando_M_Werewolf",
            7: "CID_288_Athena_Commando_M_IceKing",
            8: "CID_352_Athena_Commando_F_Shiny",
            9: "CID_407_Athena_Commando_M_BattleSuit",
            10: "CID_484_Athena_Commando_M_KnightRemix",
            11: "CID_572_Athena_Commando_M_Viper",
            12: "CID_694_Athena_Commando_M_CatBurglar",
            13: "CID_767_Athena_Commando_F_BlackKnight"
        }

        await self.party.me.set_outfit(asset=max_tier_skins[br_season])

        await ctx.send(f'Skin set to {max_tier_skins[br_season]}!')
        print(f"Skin set to {max_tier_skins[br_season]}.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client to a random Henchman skin.",
        help="Sets the outfit of the client to a random Henchman skin.\n"
             "Example: !henchman"
    )
    async def henchman(self, ctx: fortnitepy.ext.commands.Context) -> None:
        random_henchman = py_random.choice(
            "CID_794_Athena_Commando_M_HenchmanBadShorts_D",
            "CID_NPC_Athena_Commando_F_HenchmanSpyDark",
            "CID_791_Athena_Commando_M_HenchmanGoodShorts_D",
            "CID_780_Athena_Commando_M_HenchmanBadShorts",
            "CID_NPC_Athena_Commando_M_HenchmanGood",
            "CID_692_Athena_Commando_M_HenchmanTough",
            "CID_707_Athena_Commando_M_HenchmanGood",
            "CID_792_Athena_Commando_M_HenchmanBadShorts_B",
            "CID_793_Athena_Commando_M_HenchmanBadShorts_C",
            "CID_NPC_Athena_Commando_M_HenchmanBad",
            "CID_790_Athena_Commando_M_HenchmanGoodShorts_C",
            "CID_779_Athena_Commando_M_HenchmanGoodShorts",
            "CID_NPC_Athena_Commando_F_RebirthDefault_Henchman",
            "CID_NPC_Athena_Commando_F_HenchmanSpyGood",
            "CID_706_Athena_Commando_M_HenchmanBad",
            "CID_789_Athena_Commando_M_HenchmanGoodShorts_B"
        )

        await self.party.me.set_outfit(
            asset=random_henchman
        )

        await ctx.send(f'Skin set to {random_henchman}!')
        print(f"Skin set to {random_henchman}.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the emote of the client to Floss.",
        help="Sets the emote of the client to Floss.\n"
             "Example: !floss"
    )
    async def floss(self, ctx: fortnitepy.ext.commands.Context) -> None:
        # // You caused this FunGames, you caused this...
        await self.party.me.set_emote(
            asset='EID_Floss'
        )

        await ctx.send('Emote set to Floss!')
        print(f"Emote set to Floss.")

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client to a random marauder skin.",
        help="Sets the outfit of the client to a random marauder skin.\n"
             "Example: !marauder"
    )
    async def marauder(self, ctx: fortnitepy.ext.commands.Context) -> None:
        random_marauder = py_random.choice(
            "CID_NPC_Athena_Commando_M_MarauderHeavy",
            "CID_NPC_Athena_Commando_M_MarauderElite",
            "CID_NPC_Athena_Commando_M_MarauderGrunt"
        )

        await self.party.me.set_outfit(
            asset=random_marauder
        )

        await ctx.send(f'Skin set to {random_marauder}!')
        print(f"Skin set to {random_marauder}.")

    @commands.dm_only()
    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client to Golden Brutus "
                    "(shortcut for !enlightened CID_692_Athena_Commando_M_HenchmanTough 2 180).",
        help="Sets the outfit of the client to Golden Brutus.\n"
             "Example: !goldenbrutus"
    )
    async def goldenbrutus(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(
            asset='CID_692_Athena_Commando_M_HenchmanTough',
            variants=self.party.me.create_variants(progressive=4),
            enlightenment=(2, 180)
        )

        await ctx.send(f'Skin set to Golden Brutus.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client to Golden Meowscles "
                    "(shortcut for !enlightened CID_693_Athena_Commando_M_BuffCat 2 220).",
        help="Sets the outfit of the client to Golden Meowscles.\n"
             "Example: !goldenmeowscles"
    )
    async def goldenmeowscles(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(
            asset='CID_693_Athena_Commando_M_BuffCat',
            variants=self.party.me.create_variants(progressive=4),
            enlightenment=(2, 220)
        )

        await ctx.send(f'Skin set to Golden Meowscles.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client to Golden Midas "
                    "(shortcut for !enlightened CID_694_Athena_Commando_M_CatBurglar 2 140).",
        help="Sets the outfit of the client to Golden Peely.\n"
             "Example: !goldenmidas"
    )
    async def goldenmidas(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(
            asset='CID_694_Athena_Commando_M_CatBurglar',
            variants=self.party.me.create_variants(progressive=4),
            enlightenment=(2, 140)
        )

        await ctx.send(f'Skin set to Golden Midas.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client to Golden Skye "
                    "(shortcut for !enlightened CID_690_Athena_Commando_F_Photographer 2 300).",
        help="Sets the outfit of the client to Golden Skye.\n"
             "Example: !goldenskye"
    )
    async def goldenskye(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(
            asset='CID_690_Athena_Commando_F_Photographer',
            variants=self.party.me.create_variants(progressive=4),
            enlightenment=(2, 300)
        )

        await ctx.send(f'Skin set to Golden Skye.')

    @commands.dm_only()
    @commands.command(
        description="[Cosmetic] Sets the outfit of the client to Golden TNTina "
                    "(shortcut for !enlightened CID_691_Athena_Commando_F_TNTina 2 350).",
        help="Sets the outfit of the client to Golden TNTina.\n"
             "Example: !goldentntina"
    )
    async def goldentntina(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(
            asset='CID_691_Athena_Commando_F_TNTina',
            variants=self.party.me.create_variants(progressive=7),
            enlightenment=(2, 260)
        )

        await ctx.send(f'Skin set to Golden TNTina.')

    @commands.dm_only()
    @commands.command(
        description="[Client] Sends and sets the status to away.",
        help="Sends and sets the status to away.\n"
             "Example: !away"
    )
    async def away(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.set_presence(
            status=self.status,
            away=fortnitepy.AwayStatus.AWAY
        )

        await ctx.send('Status set to away.')

if os.getenv("EMAIL") and os.getenv("PASSWORD"):
    bot = SilverBot(
        email=os.getenv("EMAIL"),
        password=os.getenv("PASSWORD")
    )

    bot.run()
else:
    sys.stderr.write("ERROR: Please enter email and password in the \".env\" file.\n")
    sys.exit()
