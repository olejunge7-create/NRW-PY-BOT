import discord
from discord.ext import commands

class TicketModal(discord.ui.Modal, title="Support-Ticket erstellen"):
    reason = discord.ui.TextInput(
        label="Grund für das Ticket",
        style=discord.TextStyle.long,
        placeholder="Beschreibe dein Anliegen kurz...",
        required=True,
        max_length=300
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"Support-Ticket von {interaction.user.display_name}",
            description=f"**Grund:** {self.reason.value}",
            color=discord.Color.blue()
        )
        
        close_view = CloseTicketView()
        await channel.send(f"{interaction.user.mention} Dein Ticket wurde erstellt!", embed=embed, view=close_view)
        await interaction.response.send_message(f"Dein Ticket wurde erstellt: {channel.mention}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Ticket schließen", style=discord.ButtonStyle.red, custom_id="close_ticket_button")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket wird in 5 Sekunden gelöscht...", ephemeral=True)
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Ticket öffnen", style=discord.ButtonStyle.green, custom_id="open_ticket_button")
    async def open_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal())

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # Registriert die Views permanent, damit Buttons nach Neustarts aktiv bleiben
        self.bot.add_view(TicketView())
        self.bot.add_view(CloseTicketView())

async def setup(bot):
    await bot.add_cog(TicketCog(bot))