import discord
from discord import app_commands
from discord.ext import commands

# ==========================================
# 1. BEREICH FÜR DIE USER (BEWERBEN)
# ==========================================

class ApplicationModal(discord.ui.Modal, title="Deine Teambewerbung"):
    alter = discord.ui.TextInput(label="Wie alt bist du?", style=discord.TextStyle.short, required=True)
    erfahrung = discord.ui.TextInput(label="Hast du bereits Erfahrungen?", style=discord.TextStyle.paragraph, required=True)
    warum = discord.ui.TextInput(label="Warum möchtest du ins Team?", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        # 1. Bestätigung an den User (als DM)
        try:
            await interaction.user.send("✅ Deine Bewerbung wurde erfolgreich eingereicht! Wir prüfen diese und melden uns bei dir.")
        except discord.Forbidden:
            pass # Falls der User DMs deaktiviert hat
            
        await interaction.response.send_message("✅ Deine Bewerbung wurde erfolgreich an das Team gesendet!", ephemeral=True)
        
        # 2. Bewerbung ins Admin-Dashboard senden (Kanal: 1534552376911073451)
        # Wir müssen den Kanal über das Guild-Objekt holen
        admin_channel = interaction.guild.get_channel(1534552376911073451)
        if admin_channel:
            embed = discord.Embed(
                title="📄 Neue Bewerbung eingegangen!",
                color=discord.Color.gold()
            )
            embed.add_field(name="Bewerber", value=interaction.user.mention, inline=False)
            embed.add_field(name="Alter", value=self.alter.value, inline=False)
            embed.add_field(name="Erfahrungen", value=self.erfahrung.value, inline=False)
            embed.add_field(name="Warum ins Team?", value=self.warum.value, inline=False)
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            
            await admin_channel.send(embed=embed)

class UserApplyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="📝 Jetzt Bewerben", style=discord.ButtonStyle.primary, custom_id="persistent_user_apply_btn")
    async def apply_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApplicationModal())

# ==========================================
# 2. BEREICH FÜR DIE ADMINS (DASHBOARD)
# ==========================================

class BewerbungsModal(discord.ui.Modal, title="Bewerbungs-Entscheidung"):
    grund = discord.ui.TextInput(
        label="Grund / Feedback",
        style=discord.TextStyle.paragraph,
        placeholder="Schreibe hier den Grund für die Annahme/Ablehnung...",
        required=True,
        max_length=500
    )

    def __init__(self, action_type: str, member: discord.Member):
        super().__init__()
        self.action_type = action_type
        self.member = member

    async def on_submit(self, interaction: discord.Interaction):
        if self.action_type == "accept":
            embed = discord.Embed(title="🎉 Bewerbung Angenommen!", description=f"Glückwunsch {self.member.mention}! Deine Bewerbung wurde angenommen.\n\n**Grund/Feedback:**\n{self.grund.value}", color=discord.Color.green())
            status_text = "angenommen"
        else:
            embed = discord.Embed(title="❌ Bewerbung Abgelehnt", description=f"Hallo {self.member.mention}, leider wurde deine Bewerbung abgelehnt.\n\n**Grund/Feedback:**\n{self.grund.value}", color=discord.Color.red())
            status_text = "abgelehnt"

        embed.set_footer(text=f"Entscheidung von {interaction.user.name}")
        
        await interaction.response.send_message(f"✅ Bewerbung erfolgreich als **{status_text}** markiert. Der User wurde informiert!", ephemeral=True)
        
        try:
            await self.member.send(embed=embed)
        except discord.Forbidden:
            pass

class BewerbungsSelect(discord.ui.Select):
    def __init__(self, action_type: str):
        self.action_type = action_type
        super().__init__(placeholder="Wähle den Bewerber aus...", min_values=1, max_values=1, options=[discord.SelectOption(label="Lade Mitglieder...", value="placeholder")])

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none" or self.values[0] == "placeholder":
            await interaction.response.send_message("⚠️ Ungültige Auswahl!", ephemeral=True)
            return

        selected_id = int(self.values[0])
        member = interaction.guild.get_member(selected_id)
        if not member:
            await interaction.response.send_message("⚠️ Mitglied nicht gefunden!", ephemeral=True)
            return

        await interaction.response.send_modal(BewerbungsModal(self.action_type, member))

class BewerbungsSelectView(discord.ui.View):
    def __init__(self, action_type: str, guild: discord.Guild):
        super().__init__(timeout=60)
        self.select = BewerbungsSelect(action_type)
        
        options = []
        for member in guild.members[:25]:
            if not member.bot:
                options.append(discord.SelectOption(label=member.display_name, value=str(member.id)))
        
        if not options:
            options.append(discord.SelectOption(label="Keine Mitglieder gefunden", value="none"))

        self.select.options = options
        self.add_item(self.select)

class DashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📄 Bewerbung annehmen", style=discord.ButtonStyle.green, custom_id="dashboard_accept_btn", row=0)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = BewerbungsSelectView("accept", interaction.guild)
        await interaction.response.send_message("Wähle das Mitglied aus, dessen Bewerbung du **annehmen** möchtest:", view=view, ephemeral=True)

    @discord.ui.button(label="❌ Bewerbung ablehnen", style=discord.ButtonStyle.red, custom_id="dashboard_reject_btn", row=0)
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = BewerbungsSelectView("reject", interaction.guild)
        await interaction.response.send_message("Wähle das Mitglied aus, dessen Bewerbung du **ablehnen** möchtest:", view=view, ephemeral=True)

class DashboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="daschbord", description="Öffnet das interaktive Team-Dashboard")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def daschbord(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🛡️ TEAM DASHBOARD", description="Willkommen im Steuerungs-Panel. Aktionen wählen:", color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, view=DashboardView())

async def setup(bot):
    await bot.add_cog(DashboardCog(bot))