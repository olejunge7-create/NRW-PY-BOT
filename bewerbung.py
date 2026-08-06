import discord
from discord.ext import commands
import asyncio

QUESTIONS = [
    "Wie alt bist du?",
    "Welche Erfahrungen hast du bereits gesammelt?",
    "Warum möchtest du in unser Team?",
    "Wie viel Zeit kannst du pro Woche investieren?"
]

class BewerbungModal(discord.ui.Modal, title="Team-Bewerbung"):
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Check deine Privatnachrichten (DMs), um die Bewerbungsfragen zu beantworten!", ephemeral=True)
        
        user = interaction.user
        try:
            dm_channel = await user.create_dm()
            await dm_channel.send("👋 Hallo! Schön, dass du dich bewirbst. Ich stelle dir jetzt ein paar Fragen nacheinander. Antworte einfach hier im Chat darauf.")
        except discord.Forbidden:
            return

        answers = []
        for i, q in enumerate(QUESTIONS):
            await dm_channel.send(f"**Frage {i+1} von {len(QUESTIONS)}:**\n{q}")
            
            def check(m):
                return m.author == user and isinstance(m.channel, discord.DMChannel)

            try:
                msg = await interaction.client.wait_for('message', check=check, timeout=300.0)
                answers.append(msg.content)
            except asyncio.TimeoutError:
                await dm_channel.send("❌ Die Bewerbung wurde abgebrochen, da du zu lange (über 5 Minuten) nicht geantwortet hast.")
                return

        await dm_channel.send("✅ **Vielen Dank!** Deine Bewerbung wurde komplett ausgefüllt und an das Team weitergeleitet.")

        # Admin/Team Kanal Benachrichtigung (ID anpassen falls nötig)
        admin_channel = interaction.client.get_channel(1534552376911073451)
        if admin_channel:
            embed = discord.Embed(
                title=f"📝 Neue Bewerbung: {user.display_name}",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            for i in range(len(QUESTIONS)):
                embed.add_field(name=QUESTIONS[i], value=answers[i], inline=False)
            await admin_channel.send(embed=embed)

class BewerbungView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Bewerben", style=discord.ButtonStyle.blurple, custom_id="apply_button_persistent")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BewerbungModal())

class BewerbungCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(BewerbungView())

async def setup(bot):
    await bot.add_cog(BewerbungCog(bot))