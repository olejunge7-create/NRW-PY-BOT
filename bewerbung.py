import discord
from discord.ext import commands

class BewerbungsModal(discord.ui.Modal, title="Team-Bewerbung"):
    alter = discord.ui.TextInput(
        label="Wie alt bist du?",
        style=discord.TextStyle.short,
        placeholder="Dein Alter...",
        required=True,
        max_length=3
    )
    erfahrung = discord.ui.TextInput(
        label="Hast du Vorkenntnisse?",
        style=discord.TextStyle.paragraph,
        placeholder="Beschreibe kurz deine Erfahrungen...",
        required=True,
        max_length=500
    )
    warum = discord.ui.TextInput(
        label="Warum möchtest du ins Team?",
        style=discord.TextStyle.paragraph,
        placeholder="Deine Motivation...",
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Bestätigung für den User
        await interaction.response.send_message("✅ Deine Bewerbung wurde erfolgreich abgesendet!", ephemeral=True)
        
        try:
            await interaction.user.send("✅ Deine Bewerbung ist eingegangen und wird vom Team geprüft!")
        except discord.Forbidden:
            pass

        # Hier kannst du die Bewerbung z.B. auch in einen Admin-Kanal senden lassen, 
        # falls gewünscht, oder sie bleibt im Log. Hier posten wir sie direkt als Embed in den Kanal oder an den Bot.
        embed = discord.Embed(
            title="📄 Neue Bewerbung eingegangen!",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="Alter", value=self.alter.value, inline=False)
        embed.add_field(name="Erfahrungen", value=self.erfahrung.value, inline=False)
        embed.add_field(name="Motivation", value=self.warum.value, inline=False)
        
        # Sendet die Bewerbung zurück in denselben Kanal oder einen speziellen Auswertungs-Kanal
        await interaction.channel.send(embed=embed)

class BewerbungView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Bleibt nach Neustarts aktiv

    @discord.ui.button(label="📝 Jetzt Bewerben", style=discord.ButtonStyle.primary, custom_id="persistent_bewerbung_create_btn")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BewerbungsModal())

class BewerbungCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(BewerbungCog(bot))