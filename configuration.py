import discord
from api import gui, users, config

logging_config = config.get()

class ConfigButton(gui.MenuGUI):
    def __init__(self, interaction, _ = None, page = 1):
        super().__init__(interaction=interaction,
                         element_count=len(logging_config["logs"].keys()),
                         interaction_permission="sonny_logging:log_admin"
                         )
        groups = list(logging_config["logs"].keys())
        groups = groups[((page-1)*10):(page*10)]
        for logging_group in groups:
            buttonstyle = discord.ButtonStyle.primary
            button = discord.ui.Button(label = logging_group, style=buttonstyle, custom_id=logging_group)
            button.callback = self.open_modal_button_callback
            self.add_item(button)

        button = discord.ui.Button(label="New Group", custom_id="new", row=4)
        button.callback = self.new_group
        self.add_item(button)
    
    async def open_modal_button_callback(self, interaction: discord.Interaction):
        if not await users.has_permission(interaction.user.id, "sonny_logging:log_admin"):
            return await interaction.response.send_message(":warning: No permission.", ephemeral=True)
        group = interaction.data["custom_id"]

        view = ConfigSubButton(self.interaction, group, self.page)
        if logging_config["logs"][group][0] == 0:
            content = "Channel: None"
        else:
            content = f"Channel: <#{logging_config["logs"][group][0]}>"
        await self.interaction.edit_original_response(content=content, view=view)
        await interaction.response.defer(ephemeral=True, thinking=False)

    async def new_group(self, interaction: discord.Interaction):
        if not await users.has_permission(interaction.user.id, "sonny_logging:log_admin"):
            return await interaction.response.send_message(":warning: No permission.", ephemeral=True)
        return await interaction.response.send_modal(NewLogGroup(self.interaction))
            
class ConfigSubButton(gui.MenuGUI):
    def __init__(self, interaction, data_transfer = None, page = 1):
        super().__init__(interaction = interaction,
                         element_count = len(logging_config["logs"][data_transfer][1:]),
                         data_transfer = data_transfer,
                         interaction_permission="sonny_logging:log_admin"
                         )
        buttonstyle = discord.ButtonStyle.primary
        logs = logging_config["logs"][self.data_transfer][1:][((page-1)*10):(page*10)]
        for log in logs:
            log_formatted = log.replace("_", " ").title()
            button = discord.ui.Button(label = log_formatted, style=buttonstyle, custom_id=log)
            button.callback = self.open_modal_button_callback
            self.add_item(button)
        
        button = discord.ui.Button(label = "New Action", custom_id="new", row=4)
        button.callback = self.new_action
        self.add_item(button)
        button = discord.ui.Button(label = "Delete Group", custom_id="del", row=4)
        button.callback = self.delete
        self.add_item(button)
        button = discord.ui.Button(label = "Back", custom_id="back", row=4)
        button.callback = self.back
        self.add_item(button)

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Select the channel...",
        channel_types=[discord.ChannelType.text],
        min_values=1,
        max_values=1
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        if not await users.has_permission(interaction.user.id, "sonny_logging:log_admin"):
            return await interaction.response.send_message(":warning: No permission.", ephemeral=True)
        channel = select.values[0] 
        await interaction.response.defer(ephemeral=True, thinking=False)
        logging_config["logs"][self.data_transfer][0] = channel.id
        for log in logging_config["logs"][self.data_transfer][1:]:
            logging_config["logged_actions"][log] = channel.id
        content = f"Channel: <#{logging_config["logs"][self.data_transfer][0]}>"
        await self.interaction.edit_original_response(content=content)
        config.overwrite(logging_config)

    async def open_modal_button_callback(self, interaction: discord.Interaction):
        if not await users.has_permission(interaction.user.id, "sonny_logging:log_admin"):
            return await interaction.response.send_message(":warning: No permission.", ephemeral=True)
        old_interaction = self.interaction
        log = interaction.data["custom_id"]
        logging_config["logs"][self.data_transfer].remove(log)
        logging_config["logged_actions"].pop(log)
        logging_config["unlogged_actions"].append(log)
        config.overwrite(logging_config)
        
        view = ConfigSubButton(old_interaction, self.group)
        if logging_config["logs"][self.data_transfer][0] == 0:
            content = "Channel: None"
        else:
            content = f"Channel: <#{logging_config["logs"][self.group][0]}>"
        await old_interaction.edit_original_response(content=content, view=view)
        await interaction.response.defer(ephemeral=True, thinking=False)
    
    async def back(self, interaction: discord.Interaction):
        if not await users.has_permission(interaction.user.id, "sonny_logging:log_admin"):
            return await interaction.response.send_message(":warning: No permission.", ephemeral=True)
        view = ConfigButton(self.interaction, self.page)
        await self.interaction.edit_original_response(content="", view=view)
        await interaction.response.defer(ephemeral=True, thinking=False)

    async def new_action(self, interaction: discord.Interaction):
        if not await users.has_permission(interaction.user.id, "sonny_logging:log_admin"):
            return await interaction.response.send_message(":warning: No permission.", ephemeral=True)
        view = NewAction(self.interaction, self.data_transfer)
        await self.interaction.edit_original_response(content="", view=view)
        await interaction.response.defer(ephemeral=True, thinking=False)
    
    async def delete(self, interaction: discord.Interaction):
        if not await users.has_permission(interaction.user.id, "sonny_logging:log_admin"):
            return await interaction.response.send_message(":warning: No permission.", ephemeral=True)
        view = DeleteConfirm(self.interaction, self.data_transfer, self.page)
        await self.interaction.edit_original_response(content="Are you sure?",view=view)
        await interaction.response.defer(ephemeral=True, thinking=False)

class NewLogGroup(discord.ui.Modal, title="Create new group"):
    def __init__(self, old_interaction):
        super().__init__()
        self.old_interaction = old_interaction
        self.user_input = discord.ui.TextInput(
            label=f"Enter group name",
            placeholder="",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.user_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        value = self.user_input.value
        old_interaction = self.old_interaction
        if value in ["new", "page1", "back1", "select", "next1", "last"]:
            return await interaction.response.send_message("Sorry, that name is reserved.", ephemeral=True)
        if value in logging_config["logs"].keys():
            return await interaction.response.send_message("Name already in use.", ephemeral=True)
        logging_config["logs"][value] = [0]
        config.overwrite(logging_config)
        view = ConfigSubButton(old_interaction, value)
        await old_interaction.edit_original_response(content="", view=view)
        return await interaction.response.defer(ephemeral=True, thinking=False)

class DeleteConfirm(discord.ui.View):
    def __init__(self, old_interaction: discord.Interaction, group, page):
        super().__init__(timeout=None)
        self.old_interaction = old_interaction
        self.group = group
        self.page = page
        button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.success, custom_id="yes")
        button.callback = self.confirmation
        self.add_item(button)
        button = discord.ui.Button(label="No", style=discord.ButtonStyle.danger, custom_id="no")
        button.callback = self.back
        self.add_item(button)

    async def confirmation(self, interaction: discord.Interaction):
        if not await users.has_permission(interaction.user.id, "sonny_logging:log_admin"):
            return await interaction.response.send_message(":warning: No permission.", ephemeral=True)
        for action in logging_config["logs"][self.group][1:]:
            logging_config["unlogged_actions"].append(action)
            logging_config["logged_actions"].pop(action)
        logging_config["logs"].pop(self.group)
        config.overwrite(logging_config)
        view = ConfigButton(self.old_interaction, self.page)
        await self.old_interaction.edit_original_response(content="", view=view)
        await interaction.response.defer(ephemeral=True, thinking=False)

    async def back(self, interaction: discord.Interaction):
        if not await users.has_permission(interaction.user.id, "sonny_logging:log_admin"):
            return await interaction.response.send_message(":warning: No permission.", ephemeral=True)
        view = ConfigSubButton(self.old_interaction, self.group, self.page)
        if logging_config["logs"][self.group][0] == 0:
            content = "Channel: None"
        else:
            content = f"Channel: <#{logging_config["logs"][self.group][0]}>"
        await self.old_interaction.edit_original_response(content=content, view=view)
        await interaction.response.defer(ephemeral=True, thinking=False)

class NewAction(gui.MenuGUI):
    def __init__(self, interaction, data_transfer, page = 1):
        super().__init__(interaction=interaction,
                         element_count=len(logging_config["unlogged_actions"]),
                         data_transfer=data_transfer,
                         page = page,
                         interaction_permission="sonny_logging:log_admin"
                         )
        actions = logging_config["unlogged_actions"][((page-1)*10):(page*10)]
        for action in actions:
            action_styled = action.replace("_", " ").title()
            buttonstyle = discord.ButtonStyle.primary
            button = discord.ui.Button(label = action_styled, style=buttonstyle, custom_id=action)
            button.callback = self.open_modal_button_callback
            self.add_item(button)

        button = discord.ui.Button(label = "Back", custom_id="back", row=4)
        button.callback = self.back
        self.add_item(button)

    async def open_modal_button_callback(self, interaction: discord.Interaction):
        if not await users.has_permission(interaction.user.id, "sonny_logging:log_admin"):
            return await interaction.response.send_message(":warning: No permission.", ephemeral=True)
        action = interaction.data["custom_id"]
        
        logging_config["unlogged_actions"].remove(action)
        logging_config["logged_actions"][action] = logging_config["logs"][self.data_transfer][0]
        logging_config["logs"][self.data_transfer].append(action)
        config.overwrite(logging_config)
        await self.back(interaction)
        
    async def back(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=False)
        view = ConfigSubButton(self.interaction, self.data_transfer)
        if logging_config["logs"][self.data_transfer][0] == 0:
            self.text = "Channel: None"
        else:
            self.text = f"Channel: <#{logging_config["logs"][self.data_transfer][0]}>"
        await self.interaction.edit_original_response(content=self.text, view=view)
