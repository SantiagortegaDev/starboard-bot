import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import emoji

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(intents=intents, command_prefix=None)

class checkcontainer(discord.ui.LayoutView):
    container1=discord.ui.Container(
        discord.ui.TextDisplay(content="<:check:1566080822141001929> **Config Saved**"),
        )


class configstylemodal(discord.ui.Modal, title="Config Style"):
    def __init__(self, radio1, radio2):
        super().__init__()

        self.description = discord.ui.TextDisplay(
                content="**Configure the Starboard style**\n-# To modify the emoji use **/config-stars**")
        if "forward_message" in radio1:
            defaultforward= True
            defaultscreenshot = False
            defaultwebhook = False
        elif "screenshot" in radio1:
            defaultforward = False
            defaultscreenshot= True   
            defaultwebhook=False
        elif "webhook" in radio1:
            defaultforward = False
            defaultscreenshot= False 
            defaultwebhook=True  
        else:
            defaultforward=False
            defaultscreenshot = False
            defaultwebhook = False   
        self.radio= discord.ui.Label(text="Style of the message", component=discord.ui.RadioGroup(required=True, options=[
            discord.RadioGroupOption(
                label="Forward the message", description="The author does not appear in the starboard", custom_id="forward_message", default=defaultforward
            ),
            discord.RadioGroupOption(
                label="Generate a screenshot", description="The bot generate a screenshot of the message with the author", custom_id="screenshot", default=defaultscreenshot
            ),
            discord.RadioGroupOption(
                label="Send it with a webhook", description="Send a webhook with the author avatar and the message content", custom_id="webhook", default=defaultwebhook
            )
            ]))

        if "dont_show" in radio2:
            defaultdontshow=True
            defaultdisabledbutton=False
            defaultlittletext=False
        elif "disabled_button" in radio2:
            defaultdontshow=False
            defaultdisabledbutton=True
            defaultlittletext=False
        elif "little_text" in radio2:
            defaultdontshow=False
            defaultdisabledbutton=False
            defaultlittletext=True 

        self.radio2 = discord.ui.Label(text="Config reaction count", 
                                       component=discord.ui.RadioGroup(required=True, options=[
                                                                       discord.RadioGroupOption(
                                                                           label="Don't show the count", description="Hide the reaction count from the starboard", custom_id="dont_show", default=defaultdontshow
                                                                       ),
                                                                       discord.RadioGroupOption(
                                                                           label="Disabled button", description="A disabled button with the reaction count", custom_id="disabled_button", default=defaultdisabledbutton
                                                                       ),
                                                                       discord.RadioGroupOption(
                                                                           label="Little text", description="the bot will send a little text below the message forwared", custom_id="little_text", default=defaultlittletext
                                                                       )]
                                                                       )
                                                                       )

        self.add_item(self.description)
        self.add_item(self.radio)
        self.add_item(self.radio2)
    async def on_submit(self, interaction: discord.Interaction):
        editconfig(interaction.guild_id, "style", self.radio.component.values)
        editconfig(interaction.guild_id, "style_count", self.radio2.component.values)
        await interaction.response.send_message(
            view=checkcontainer()
        )


class configurationmodal(discord.ui.Modal, title="Config Stars"):
    def __init__(self, interaction, channel, emoji, count, checkbox1, checkbox2, checkbox3):
        super().__init__()
        self.interaction=interaction

        self.description = discord.ui.TextDisplay(
                content="**Configure the Starboard Star options**\n-# To modify the appearance of the forwarder use **/config-style**")
        
        self.channel=discord.ui.Label(
            text="Channel to send the messages",
            component=discord.ui.ChannelSelect(
                channel_types=[discord.ChannelType.text],
                required=True,
                placeholder="Select the channel",
                default_values=channel
            )
        )
    
        self.emoji=discord.ui.Label(
            text="Emoji",
            description="In markdown",
            component=discord.ui.TextInput(
                required=True,
                style=discord.TextStyle.short,
                placeholder=":star:",
                default=emoji
            )
        )
        self.count=discord.ui.Label(
            text="How many stars?",
            description="to send the message in the starboard",
            component=discord.ui.TextInput(
                style=discord.TextStyle.short,
                required=True,
                placeholder="4",
                default=count
            )
        )
        self.checkboxes=discord.ui.Label(
        text="Extra",
        component=discord.ui.CheckboxGroup(
            options=[
                discord.CheckboxGroupOption(
                    label="Ignore author reactions",
                    value="ignore_author",
                    description="only those of others will be counted",
                    default=checkbox1
                ),
                discord.CheckboxGroupOption(
                    label="Delete message",
                    description="if the reaction count drops",
                    value="delete_message",
                    default=checkbox2
                ),
                discord.CheckboxGroupOption(
                    label="Edit message",
                    description="Sync the message content in the starboard",
                    value="edit_message",
                    default=checkbox3
                )
            ],
            required=False
        )  
)

        self.add_item(self.description)
        self.add_item(self.channel)
        self.add_item(self.emoji)
        self.add_item(self.count)
        self.add_item(self.checkboxes)
    async def on_submit(self, interaction: discord.Interaction):
        editconfig(interaction.guild_id, "channel", self.channel.component.values[0].id)
        editconfig(interaction.guild_id, "emoji", self.emoji.component.value)
        editconfig(interaction.guild_id, "count", int(self.count.component.value))
        editconfig(interaction.guild_id, "checkboxes", self.checkboxes.component.values)
        await interaction.response.send_message(
            view=checkcontainer()
        )



def readjson():
    try:
        with open("configs.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def editjson(datos):
     with open("configs.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


def readconfig(server_id):
    try:
     datos = readjson()
     return datos.get(str(server_id), {})
    except (FileNotFoundError, json.JSONDecodeError):
        editjson({})
        return {}    



def editconfig(server_id, llave, valor):
    datos = readjson()      
    config = datos.get(str(server_id), {})
    config[llave] = valor     
    datos[str(server_id)] = config
    editjson(datos)       

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot conectado como {bot.user}")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    config=readconfig(payload.guild_id)
    if "ignore_author" in str(config["checkboxes"]):
             ignore_author_reacc=True
    else:
             ignore_author_reacc=False

    if msg.author.id == payload.user_id and ignore_author_reacc == True:
        return
    count = 0
    for reaction in msg.reactions:
        if str(reaction.emoji) == str(payload.emoji):
            count = reaction.count

    print(f"{payload.user_id} reaccionó con {payload.emoji} en el mensaje {payload.message_id}")
    print(f"tiene {count} reacciones")
    markdown = payload.emoji.id
    configemoji = config["emoji"]
    if markdown == True:
            emojimarkdown = f":{payload.emoji.name}:"
    else:
            emojimarkdown = emoji.demojize(str(payload.emoji))
    if count >= int(config["count"]) and emojimarkdown in configemoji:
         print("debe estar en starboard")


@bot.event
async def on_raw_reaction_remove(payload):
    print(f"{payload.user_id} quitó {payload.emoji} del mensaje {payload.message_id}")
    if payload.user_id == bot.user.id:
            return
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    config=readconfig(payload.guild_id)
    if "delete_message" in str(config["checkboxes"]):
            delete_message=True
    else:
            delete_message=False
    count = 0
    for reaction in msg.reactions:
        if str(reaction.emoji) == str(payload.emoji):
            count = reaction.count
    configcount= int(config["count"])
    configemoji = config["emoji"]
    markdown = payload.emoji.id
    if markdown == True:
        emojimarkdown = f":{payload.emoji.name}:"
    else:
        emojimarkdown = emoji.demojize(str(payload.emoji))
    if configcount > count and delete_message == True and emojimarkdown in configemoji:
        print("el mensaje se debe eliminar")      




@bot.tree.command(name="config-stars", description="Change stars configurations")
async def hola(interaction: discord.Interaction):
    config = readconfig(interaction.guild_id)
    try:
     if config["channel"]:
         channel=[discord.SelectDefaultValue(id=int(config["channel"]), type=discord.SelectDefaultValueType.channel)]
    except:
        channel=None
    try:
     if config["emoji"]:
         emoji=config["emoji"]
    except:
     emoji=None
    try:
     if config["count"]:
         count=str(config["count"])   
    except:
        count=None
    try:
     if "delete_message" in str(config["checkboxes"]):
               checkbox2=True
     else:
         checkbox2=False
    except:
     checkbox2=False
    try:
     if "edit_message" in str(config["checkboxes"]):
         checkbox3=True
     else:
         checkbox3=False
    except:
     checkbox3=False
    try:
     if "ignore_author"  in str(config["checkboxes"]):
         checkbox1=True
     else:
         checkbox1=False            
    except:
       checkbox1=False
    await interaction.response.send_modal(configurationmodal(interaction, channel, emoji, count, checkbox1, checkbox2, checkbox3))

@bot.tree.command(name="help", description="HEEEEEEEEELP")
async def hola(interaction: discord.Interaction):
    await interaction.response.send_message()
    
@bot.tree.command(name="ping", description="pong, well you know")
async def hola(interaction: discord.Interaction):
    await interaction.response.send_message(f"**Pong**\n-# {bot.latency * 1000:.2f} ms")

@bot.tree.command(name="config-style", description="change the starboard design")
async def hola(interaction: discord.Interaction):
    config=readconfig(interaction.guild_id)
    print(config["style"])
    print(config["style_count"])
    await interaction.response.send_modal(configstylemodal())

bot.run(os.getenv("ULTRASECRETDISCORDTOKEN"))