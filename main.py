from flet import *
import os

from views.homescreen import HomeScreen
from views.searchscreen import SearchScreen
from views.libraryscreen import LibraryScreen
from views.playscreen import PlayScreen
from views.navigationbar import _NavigationBar
from data.database import DataBase


def main(page: Page):
    page.title = "Music Player"
    page.window.width = 400
    page.window.height = 700
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.theme_mode = "light"

    # Run in the first time
    DataBase.CreateDatabase()

    def toggle_play_pause_icon(e):
        e.control.selected = not e.control.selected
        e.control.update()
        audio.pause() if e.control.selected else audio.resume()
        audio.update()

    # Maximize play_screen
    def maximize(e):
        play_container.controls[0].height = 600
        play_container.controls[0].scale = transform.Scale(1, alignment=alignment.bottom_center)
        play_container.controls[0].disabled = False
        play_container.controls[0].update()

    page.fonts = {
        "YouTubeSansBold": "assets/fonts/YouTubeSansBold.otf",
        "YouTubeSansLight": "assets/fonts/YouTubeSansLight.otf",
        "Roboto-Bold": "assets/fonts/Roboto-Bold.ttf",
        "Roboto-Medium": "assets/fonts/Roboto-Medium.ttf",
        "Roboto-Italic": "assets/fonts/Roboto-Italic.ttf",
    }
    
    audio = Audio(src=os.getcwd(), autoplay=False)
    main_container = Column(spacing=0)

    main_stack = Stack(
        width=290,
        height=600,
        controls=[
            main_container,
        ]
    )

    mini_play_container = Column(
        visible=False,
        alignment="end",
        spacing=0,
        controls=[
            Container(
                bgcolor="white",
                width=290,
                height=50,
                border_radius=10,
                on_click=lambda e: maximize(e),
                content=Row(
                    spacing=0,
                    controls=[
                        Image(
                            border_radius=10,
                            width=50,
                            height=50,
                            src=os.getcwd(),
                            fit=ImageFit.FILL,
                        ),
                        Container(width=10),
                        Container(
                            width=150,
                            content=Column(
                                spacing=1,
                                controls=[
                                    Text("", font_family="Roboto-Medium",no_wrap=True),
                                    Text("", font_family="Roboto-Medium", size=13, opacity=0.8, no_wrap=True),
                                ]
                            )
                        ),
                        Container(width=30),
                        IconButton(
                            icon=icons.PAUSE_CIRCLE_ROUNDED,
                            selected_icon=icons.PLAY_CIRCLE_ROUNDED,
                            selected=False,
                            icon_size=32,
                            on_click=lambda e: toggle_play_pause_icon(e)
                        ),
                    ]
                )
            )
        ]
    )

    play_screen = PlayScreen(audio, mini_play_container, main_stack)
    library_screen = LibraryScreen(play_screen, main_stack)

    play_container = Column(
        alignment="end",
        controls=[
            play_screen,
        ]
    )

    search_screen = SearchScreen(play_container, main_stack, audio)
    # page.add(search_screen.progress_bar)
    home_screen = HomeScreen(search_screen, play_container, main_stack)
    _navigation_bar = _NavigationBar(home_screen, search_screen, library_screen)

    main_container.controls.append(           
        Container(
            width=290,
            height=560,
            bgcolor="#111827" if page.theme_mode=="dark" else "#9999ff",
            padding=padding.only(bottom=0),
            border_radius=border_radius.only(top_left=25, top_right=25),  
            content=Stack(
                controls=[
                    home_screen,
                    search_screen,
                    library_screen,
                    mini_play_container,
                ]
            )
        )
    )
    
    main_container.controls.append(           
        Container(
            bgcolor="#111827" if page.theme_mode=="dark" else "#9999ff",
            border_radius=border_radius.only(bottom_left=25, bottom_right=25),  
            content=_navigation_bar,
        )
    )
    page.update()

    page.add(main_stack)

app(target=main)
