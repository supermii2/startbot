import discord

from utils.string_utils import list_to_str


class MultipleSelect:
    PAGE_SIZE = 25

    class _MultiSelectPage(discord.ui.Select):
        def __init__(self, parent, options: list[discord.SelectOption]):
            self.parent = parent
            self.current_values = []
            super().__init__(options=options)

        async def callback(self, interaction: discord.Interaction):
            self.parent.num_selectable = self.parent.num_selectable - len(self.values) + len(self.current_values)
            self.current_values = self.values
            s = "You have selected: " + list_to_str(self.parent.find_all_values())
            await interaction.response.edit_message(content=s)

    class _ArrowButton(discord.ui.Button):
        def __init__(self, parent, is_left: bool):
            self.parent, self.is_left = parent, is_left
            super().__init__(label="<-" if is_left else "->", style=discord.ButtonStyle.grey)

        async def callback(self, interaction: discord.Interaction):
            self.parent.update_page(self.is_left)
            await interaction.response.edit_message(view=self.parent.view)

    class _ConfirmButton(discord.ui.Button):
        def __init__(self, parent):
            self.parent = parent
            super().__init__(label="Confirm", style=discord.ButtonStyle.green)

        async def callback(self, interaction: discord.Interaction):
            if self.parent.find_all_values():
                await self.parent.confirm(interaction)

    class _ClearButton(discord.ui.Button):
        def __init__(self, parent):
            self.parent = parent
            super().__init__(label="Clear", style=discord.ButtonStyle.red)

        async def callback(self, interaction: discord.Interaction):
            self.parent.clear_all_values()
            self.parent.update_view()
            await interaction.response.edit_message(content="You have selected: ", view=self.parent.view)

    def __init__(self, options: list[discord.SelectOption], view: discord.ui.View, limit=1):
        self.view = view
        self.original_limit, self.num_selectable = limit, limit
        self.values = []
        self.current_page = 0
        self.pages = self._init_pages(options)
        self.buttons = [MultipleSelect._ArrowButton(self, True),
                        MultipleSelect._ConfirmButton(self),
                        MultipleSelect._ArrowButton(self, False),
                        MultipleSelect._ClearButton(self)]

        self.update_view()

    def _init_pages(self, options: list[discord.SelectOption]) -> list[_MultiSelectPage]:
        num_pages = ((len(options) - 1) // MultipleSelect.PAGE_SIZE) + 1
        pages = []
        for i in range(num_pages):
            start_index = i * MultipleSelect.PAGE_SIZE
            end_index = (i + 1) * MultipleSelect.PAGE_SIZE
            pages.append(MultipleSelect._MultiSelectPage(self, options[start_index:end_index]))
        return pages

    async def confirm(self, interaction):
        """This method is intended to be overridden by child classes"""
        pass

    def update_view(self):
        self.view.clear_items()
        page = self.pages[self.current_page]
        page.disabled = True if self.num_selectable == 0 else False
        if self.num_selectable != 0:
            page.max_values = self.num_selectable
        self.pages[self.current_page].placeholder = f"Page {str(self.current_page + 1)} of {str(len(self.pages))}"
        self.view.add_item(self.pages[self.current_page])
        for button in self.buttons:
            self.view.add_item(button)

    def update_page(self, is_left):
        self.current_page = (self.current_page - 1) % len(self.pages) if is_left else (self.current_page + 1) % len(
            self.pages)
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
