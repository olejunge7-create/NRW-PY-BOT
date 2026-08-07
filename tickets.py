import discord
from discord.ext import commands
import asyncio

def get_allowed_roles(guild, min_role_id):
    min_role = guild.get_role(min_role_id)
    if not min_role:
        return []
    # Gibt die angegebene Rolle und alle Rollen, die darüber stehen, zurück
    return [role for role in guild.roles if role.position >= min_role.position]

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support & Fragen", description="Allgemeine Anfragen", emoji="🎫"),
            discord.SelectOption(label="Team-Bewerbungen", description="Bewirb dich für unser Team", emoji="🧑‍💻"),
            discord.SelectOption(label="Partner-Anfragen", description="Frage eine Partnerschaft an", emoji="🤝"),
            discord.SelectOption(label="Sonstiges", description="Für alle anderen Anliegen", emoji="📂")
        ]
        super().__init__(placeholder="Ticket-Kategorie auswählen...", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        selected_label = self.values[0]
        
        # Hier weisen wir jeder Kategorie exakt deine gewünschte minimale Rollen-ID zu:
        if selected_label == "Support & Fragen":
            min_role_id = 1534325338182520992
        elif selected_label == "Sonstiges":
            min_role_id = 1534325338182520991
        elif selected_label == "Partner-Anfragen":
            min_role_id = 1534325338212007979
        elif selected_label == "Team-Bewerbungen":
            min_role_id = 1534325338199556145
        else:
            min_role_id = 0

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        # Alle berechtigten Rollen (ab der ID und höher) hinzufügen
        allowed_roles = get_allowed_roles(guild, min_role_id)
        for role in allowed_roles:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        channel_name = f"ticket-{interaction.user.name}".lower().replace(" ", "-")
        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)

        await interaction.response.send_message(f"✅ Dein Ticket wurde erstellt: {ticket_channel.mention}", ephemeral=True)

        embed = discord.Embed(
            title=f"Ticket: {selected_label}",
            description=f"Hallo {interaction.user.mention}!\nDanke für deine Anfrage. Ein Teammitglied wird sich gleich bei dir melden.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Status", value="❌ Noch nicht beansprucht", inline=False)
        
        await ticket_channel.send(embed=embed, view=TicketControlView(min_role_id))

class TicketControlView(discord.ui.View):
    def __init__(self, min_role_id):
        super().__init__(timeout=None)
        self.min_role_id = min_role_id

    @discord.ui.button(label="Ticket beanspruchen", style=discord.ButtonStyle.green, custom_id="claim_ticket_btn", emoji="🙋‍♂️")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        allowed_roles = get_allowed_roles(interaction.guild, self.min_role_id)
        is_admin = interaction.user.guild_permissions.administrator
        has_permission = is_admin or any(role in interaction.user.roles for role in allowed_roles)

        if not has_permission:
            await interaction.response.send_message("❌ Dazu hast du keine Berechtigung!", ephemeral=True)
            return

        message = interaction.message
        embed = message.embeds[0]
        embed.color = discord.Color.green()
        embed.set_field_at(0, name="Status", value=f"✅ Beansprucht von {interaction.user.mention}", inline=False)
        
        await interaction.response.edit_message(embed=embed)
        await interaction.followup.send(f"🎟️ Übernommen von {interaction.user.mention}.")

    @discord.ui.button(label="Ticket schließen", style=discord.ButtonStyle.red, custom_id="close_ticket_btn", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Ticket wird in 5 Sekunden gelöscht...", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(TicketCog(bot))