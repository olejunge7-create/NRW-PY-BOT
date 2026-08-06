import discord
from discord.ext import commands
import asyncio

TEAM_ROLE_IDS = []

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Ticket schließen", style=discord.ButtonStyle.red, custom_id="persistent_ticket_close_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Dieses Ticket wird in wenigen Sekunden gelöscht...", ephemeral=False)
        await asyncio.sleep(3)
        try:
            await interaction.channel.delete()
        except Exception:
            pass

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Ticket erstellen", style=discord.ButtonStyle.primary, custom_id="persistent_ticket_create_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user

        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{member.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"Du hast bereits ein offenes Ticket: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        for role_id in TEAM_ROLE_IDS:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{member.name}",
            overwrites=overwrites,
            topic=f"Support-Ticket von {member.name} (ID: {member.id})"
        )

        embed = discord.Embed(
            title=f"Support-Ticket | {member.display_name}",
            description="Willkommen im Support! Ein Teammitglied wird sich gleich um dich kümmern.\nKlicke auf den Button unten, um das Ticket zu schließen.",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(f"Dein Ticket wurde erstellt: {ticket_channel.mention}", ephemeral=True)
        await ticket_channel.send(content=f"{member.mention}", embed=embed, view=TicketCloseView())

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(TicketCog(bot))

