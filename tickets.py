import discord
from discord.ext import commands
import asyncio

# Deine komplette Rang-Liste von unten nach oben
ROLE_HIERARCHY = [
    1534325338182520991,  # Rang 1
    1534325338182520992,  # Rang 2
    1534325338182520993,  # Rang 3
    1534325338182520994,  # Rang 4
    1534325338199556137,  # Rang 5
    1534325338199556138,  # Rang 6
    1534325338199556139,  # Rang 7
    1534325338199556140,  # Rang 8
    1534325338199556142,  # Rang 9
    1534325338199556143,  # Rang 10
    1534325338199556145,  # Rang 11 (Teamleitung / Bewerbungen ab hier)
    1534325338199556146,  # Rang 12
    1534325338212007978,  # Rang 13
    1534325338212007979,  # Rang 14 (Partner-Anfragen ab hier)
    1534325338212007980,  # Rang 15
    1534325338212007981,  # Rang 16
    1534325338212007982,  # Rang 17
    1534325338212007983,  # Rang 18
    1534325338212007984,  # Rang 19
    1534325338212007985,  # Rang 20
    1534325338212007986,  # Rang 21
]

def get_roles_from_threshold(guild, threshold_role_id):
    try:
        threshold_index = ROLE_HIERARCHY.index(threshold_role_id)
    except ValueError:
        return []
    
    valid_ids = ROLE_HIERARCHY[threshold_index:]
    allowed_roles = []
    for r_id in valid_ids:
        role = guild.get_role(r_id)
        if role:
            allowed_roles.append(role)
    return allowed_roles

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support & Fragen", description="Ab Rang 2 und höher", emoji="🎫"),
            discord.SelectOption(label="Team-Bewerbungen", description="Ab Teamleitung (Rang 11) und höher", emoji="🧑‍💻"),
            discord.SelectOption(label="Partner-Anfragen", description="Ab Rang 14 und höher", emoji="🤝"),
            discord.SelectOption(label="Sonstiges", description="Ab Rang 1 und höher", emoji="📂")
        ]
        super().__init__(placeholder="Ticket-Kategorie auswählen...", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        selected_label = self.values[0]
        
        if selected_label == "Support & Fragen":
            min_role_id = 1534325338182520992  # Rang 2
        elif selected_label == "Sonstiges":
            min_role_id = 1534325338182520991  # Rang 1
        elif selected_label == "Partner-Anfragen":
            min_role_id = 1534325338212007979  # Rang 14
        elif selected_label == "Team-Bewerbungen":
            min_role_id = 1534325338199556145  # Rang 11
        else:
            min_role_id = ROLE_HIERARCHY[0]

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        allowed_roles = get_roles_from_threshold(guild, min_role_id)
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
        
        await ticket_channel.send(embed=embed, view=CloseTicketView(min_role_id))

# Hier heißt die Klasse wieder exakt CloseTicketView, damit bot.py sie findet
class CloseTicketView(discord.ui.View):
    def __init__(self, min_role_id=ROLE_HIERARCHY[0]):
        super().__init__(timeout=None)
        self.min_role_id = min_role_id

    @discord.ui.button(label="Ticket beanspruchen", style=discord.ButtonStyle.green, custom_id="claim_ticket_btn", emoji="🙋‍♂️")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        allowed_roles = get_roles_from_threshold(interaction.guild, self.min_role_id)
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