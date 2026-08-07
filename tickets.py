import discord
from discord.ext import commands

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support & Fragen", description="Erstelle ein Ticket für allgemeine Fragen", emoji="🎫"),
            discord.SelectOption(label="Team-Bewerbungen", description="Bewirb dich für unser Team", emoji="🧑‍💻"),
            discord.SelectOption(label="Partner-Anfragen", description="Frage eine Partnerschaft an", emoji="🤝"),
            discord.SelectOption(label="Sonstiges", description="Für alle anderen Anliegen", emoji="📂")
        ]
        super().__init__(placeholder="Ticket-Kategorie auswählen...", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category_name = self.values[0]
        
        # Erstelle einen privaten Kanal für den User
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        # Optional: Hier kannst du eine Kategorie-ID auf deinem Server angeben, wo die Tickets erstellt werden sollen (oder None)
        # ticket_category = guild.get_channel(DEINE_KATEGORIE_ID)
        
        channel_name = f"ticket-{interaction.user.name}".lower().replace(" ", "-")
        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)

        await interaction.response.send_message(f"✅ Dein Ticket wurde erstellt: {ticket_channel.mention}", ephemeral=True)

        embed = discord.Embed(
            title=f"Ticket: {category_name}",
            description=f"Hallo {interaction.user.mention}!\nDanke für deine Anfrage im Bereich **{category_name}**. Ein Teammitglied wird sich gleich bei dir melden.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(embed=embed, view=CloseTicketView())

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket schließen", style=discord.ButtonStyle.red, custom_id="close_ticket_btn", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Ticket wird in 5 Sekunden gelöscht...", ephemeral=True)
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(TicketCog(bot))