import discord

def list_to_str(lst):
    s = ""
    for x in lst:
        s += x + ", "
    return s[:-2] if s != "" else s

class MultipleSelect():
    class MultiSelectPage(discord.ui.Select):
        def __init__(self, parent, options: list[discord.SelectOption]):
            self.parent = parent
            self.current_values = []
            super().__init__(options=options)

        async def callback(self, interaction: discord.Interaction):
            self.parent.num_selectable = self.parent.num_selectable - len(self.values) + len(self.current_values)
            self.current_values = self.values
            s = "You have selected: " + list_to_str(self.parent.find_all_values())
            await interaction.response.edit_message(content=s)

    class ArrowButton(discord.ui.Button):
        def __init__(self, parent, isLeft:bool):
            self.parent, self.isLeft = parent, isLeft
            super().__init__(label="<-" if isLeft else "->", style=discord.ButtonStyle.grey)

        async def callback(self, interaction: discord.Interaction):
            self.parent.update_page(self.isLeft)
            await interaction.response.edit(view=self.parent.view)
            await interaction.response.defer()

    class ConfirmButton(discord.ui.Button):
        def __init__(self, parent):
            self.parent = parent
            super().__init__(label="Confirm", style=discord.ButtonStyle.green)

        async def callback(self, interaction: discord.Interaction):
            if (self.parent.find_all_values()) != []:
                await self.parent.confirm(interaction)

    class ClearButton(discord.ui.Button):
        def __init__(self, parent):
            self.parent = parent
            super().__init__(label="Clear", style=discord.ButtonStyle.red)
        
        async def callback(self, interaction: discord.Interaction):
            self.parent.clear_all_values()
            self.parent.update_view()
            await interaction.response.edit_message(content="You have selected: ",view=self.parent.view)
    

    def __init__(self, options: list[discord.SelectOption], view: discord.ui.View, limit=1):
        PAGE_SIZE = 25

        self.view = view
        self.current_page = 0
        self.pages = []
        self.values = []
        self.original_limit = limit
        self.num_selectable = limit

        for i in range(0, ((len(options) - 1) // PAGE_SIZE) + 1):
            self.pages.append(MultipleSelect.MultiSelectPage(self, options[i * PAGE_SIZE:(i + 1) * PAGE_SIZE]))

        self.buttons = [MultipleSelect.ArrowButton(self, True), 
                        MultipleSelect.ConfirmButton(self), 
                        MultipleSelect.ArrowButton(self, False), 
                        MultipleSelect.ClearButton(self)]
        self.update_view()

    async def confirm(self, interaction):
        pass

    def update_view(self):
        self.view.clear_items()
        page = self.pages[self.current_page]
        page.disabled = True if self.num_selectable == 0 else False
        if self.num_selectable != 0:
            page.max_values = self.num_selectable 
        self.pages[self.current_page].placeholder = "Page " + str(self.current_page + 1) + " of " + str(len(self.pages)) 
        self.view.add_item(self.pages[self.current_page])
        for button in self.buttons:
            self.view.add_item(button)

    def update_page(self, isLeft):
        self.current_page = (self.current_page - 1) % len(self.pages) if isLeft else (self.current_page + 1) % len(self.pages)
        self.update_view()

    def clear_all_values(self):
        self.num_selectable = self.original_limit
        for page in self.pages:
            page.current_values.clear()

    def find_all_values(self):
        self.values.clear()
        for page in self.pages:
            self.values.extend(page.current_values)
        return self.values