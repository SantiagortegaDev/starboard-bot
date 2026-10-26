import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(intents=intents, command_prefix=None)

class configurationmodal(discord.ui.Modal, title="Config Stars"):
    description = discord.ui.TextDisplay(
            content="**Configure the Starboard Star options**\n-# To modify the appearance of the forwarder use **/config-style**")    
    channel=discord.ui.Label(
        text="Channel to send the messages",
        component=discord.ui.ChannelSelect(
            channel_types=[discord.ChannelType.text],
            required=True,
            placeholder="Select the channel"
        )
    )

    emoji=discord.ui.Label(
        text="Emoji",
        description="In markdown",
        component=discord.ui.TextInput(
            required=True,
            style=discord.TextStyle.short,
            placeholder=":star:",
            default=":star:"
        )
    )
    count=discord.ui.Label(
        text="How many stars?",
        description="to send the message in the starboard",
        component=discord.ui.TextInput(
            style=discord.TextStyle.short,
            required=True,
            placeholder="4",
            default="4"
        )
    )
    checkboxes=discord.ui.Label(
    text="Extra",
    component=discord.ui.CheckboxGroup(
        options=[
            discord.CheckboxGroupOption(
                label="Ignore author reactions",
                value="ignore_author",
                description="only those of others will be counted"
            ),
            discord.CheckboxGroupOption(
                label="Delete message",
                description="if the reaction count drops",
                value="delete_message"
            ),
            discord.CheckboxGroupOption(
                label="Edit message",
                description="Sync the message content in the starboard",
                value="edit_message"
            )
        ],
        required=False
    )
)


    

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"channel={self.channel.component.values[0].id}\nemoji={self.emoji.component.value}\ncheckboxes={self.checkboxes.component.values}"
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
    datos = readjson()
    return datos.get(str(server_id), {})


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


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)

    if msg.author.id == payload.user_id and ignore_author_reacc == True:
        return
    
    print(f"{payload.user_id} reaccionó con {payload.emoji} en el mensaje {payload.message_id}")


@bot.event
async def on_raw_reaction_remove(payload):
    print(f"{payload.user_id} quitó {payload.emoji} del mensaje {payload.message_id}")


@bot.tree.command(name="config-stars", description="Change stars configurations")
async def hola(interaction: discord.Interaction):
    await interaction.response.send_modal(configurationmodal())

@bot.tree.command(name="help", description="HEEEEEEEEELP")
async def hola(interaction: discord.Interaction):
    await interaction.response.send_message()


@bot.tree.command(name="add-reaction", description="add a new emoji")
async def hola(interaction: discord.Interaction):
    await interaction.response.send_modal()    


bot.run(os.getenv("ULTRASECRETDISCORDTOKEN"))