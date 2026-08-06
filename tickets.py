import discord
from discord import app_commands
from discord.ext import commands
import io

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Allgemeine Frage", description="Fragen zum Server oder Konzept", emoji="❓", value="frage"),
            discord.SelectOption(label="Team-Beschwerde", description="Beschwerde über ein Teammitglied", emoji="🛡️", value="beschwerde"),
            discord.SelectOption(label="Bug / Fehler", description="Melde einen Fehler im System oder Server", emoji="🐛", value="bug"),
            discord.SelectOption(label="Partnerschaft", description="Anfrage für Kooperationen", emoji="🤝", value="partner")
        ]
        super().__init__(placeholder="Wähle die Art deines Anliegens...", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")

        if not category:
            category = await guild.create_category("Tickets")

        # Prüfen, ob der User bereits ein offenes Ticket hat
        channel_name = f"ticket-{interaction.user.name.lower()}"
        existing_channel = discord.utils.get(category.channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message(f"⚠️ Du hast bereits ein offenes Ticket: {existing_channel.mention}", ephemeral=True)
            return

        # Berechtigungen: Nur der User, der Bot und Admins/Mods dürfen das Ticket sehen
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, manage_messages=True)
        }

        # Ticket-Kanal erstellen
        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        # Kategorie-Titel für das Embed schön aufbereiten
        grund_mapping = {
            "frage": "Allgemeine Frage",
            "beschwerde": "Team-Beschwerde",
            "bug": "Bug / Fehler",
            "partner": "Partnerschaft"
        }
        anliegen = grund_mapping.get(self.values[0], "Sonstiges")

        # Willkommens-Embed im Ticket
        embed = discord.Embed(
            title="🎫 Support-Ticket eröffnet",
            description=(
                f"Willkommen, {interaction.user.mention}!\n\n"
                f"**Anliegen:** `{anliegen}`\n\n"
                "Bitte schildere dein Problem so genau wie möglich. Ein Teammitglied wird sich in Kürze bei dir melden.\n\n"
                "Klicke unten auf **Ticket schließen**, wenn dein Anliegen geklärt ist."
            ),
            color=discord.Color.from_rgb(47, 49, 54)
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="Professionelles Support-System", icon_url=guild.icon.url if guild.icon else None)

        view = TicketCloseView()
        await ticket_channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"✅ Dein Ticket wurde erstellt: {ticket_channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket schließen", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_button")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Ticket wird geschlossen und Kanal gelöscht...", ephemeral=False)
        import asyncio
        await asyncio.sleep(3)
        await interaction.channel.delete()

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketsetup", description="Sendet das professionelle Ticket-Panel in den Kanal")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticketsetup(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🛡️ Support-Center",
            description=(
                "Benötigst du Hilfe oder hast eine Frage?\n\n"
                "Wähle im unten stehenden Menü die passende Kategorie aus, um ein **privates Ticket** zu öffnen. "
                "Unser Team wird dir schnellstmöglich weiterhelfen!"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Klicke auf das Menü, um zu starten.")

        view = TicketView()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Professionelles Ticket-Panel erfolgreich gesendet!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))