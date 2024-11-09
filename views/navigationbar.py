from flet import *

class _NavigationBar(Tabs):
    def __init__(self, home_screen, search_screen, library_screen):
        super().__init__(
            width=290,
            height=40,
            unselected_label_color=colors.GREY_100,
            label_color=colors.PINK,
            divider_height=0,
            indicator_color="transparent",
            divider_color="transparent",
            tab_alignment=TabAlignment.CENTER,
            on_change=lambda e: self.changeTab(e),
        )
        self.home_screen = home_screen
        self.search_screen = search_screen
        self.library_screen = library_screen                                         

    def changeTab(self, e):
        index = e.control.selected_index
        if index == 0:
            self.home_screen.visible = True
            self.search_screen.visible = False
            self.library_screen.visible = False
        if index == 2:
            self.home_screen.visible = False
            self.search_screen.visible = True
            self.library_screen.visible = False
        if index == 4:
            self.home_screen.visible = False
            self.search_screen.visible = False
            self.library_screen.visible = True
        self.home_screen.update()
        self.search_screen.update()
        self.library_screen.update()

    def build(self):
        self.tabs = [
            Tab(tab_content=Icon(icons.HOME_ROUNDED)),
            Container(width=5),
            Tab(tab_content=Icon(icons.SEARCH_ROUNDED)),
            Container(width=5),
            Tab(tab_content=Icon(icons.ACCOUNT_CIRCLE_ROUNDED)),
        ]
        return self.tabs
    