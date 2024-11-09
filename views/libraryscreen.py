from flet import *
import os
import shutil

from data.database import DataBase
from views.playscreen import Song


class LibraryScreen(Container):
    def __init__(self, play_screen, main_stack):
        super().__init__(
            width=290,
            height=560,
            border_radius=border_radius.only(top_left=25, top_right=25),
            padding=padding.only(left=10, right=10),
            visible=False,
        )

        self.play_screen = play_screen
        self.main_stack = main_stack
        self.song_column = Column(scroll=ScrollMode.HIDDEN)

    def AppTitle(self):
        return Container(
            height=50,
            padding=padding.only(5),
            content=Column(
                controls=[
                    Row(
                        controls=[
                            Image(src="assets/images/logo.png", width=40),
                            Text(
                                spans=[
                                    TextSpan(
                                        "Music Player",
                                        TextStyle(
                                            size=20,
                                            weight=FontWeight.BOLD,
                                            foreground=Paint(
                                                gradient=PaintLinearGradient(
                                                    begin=(0, 20), 
                                                    end=(180, 20), 
                                                    color_stops = [0.1, 0.5, 0.9],
                                                    colors=["orange", "pink", "purple"],
                                                )
                                            ),
                                        ),
                                    ),
                                ],
                            )
                        ]
                    ),
                    Divider(height=5, color="transparent"),
                ]
            )
        )

    def Heading(self):
        return Container(
            height=40,
            content=Column(
                alignment=alignment.center,
                controls=[
                    Text("Your favorite songs", font_family="Roboto-Bold", size=16),
                ]
            )
        )
    
    def upload_song_from_database(self):        
        db = DataBase.ConectToDatabase()
        
        for item in DataBase.ReadDatabase(db):
            # Copy audio file from library to mymusic
            shutil.copy(item[0], "assets/mymusic")

            # Append song
            self.song_column.controls.append(
                Song(item[0], item[1], item[2], item[3], item[4], item[5], self.play_screen, self.main_stack)
            )
        db.close()

    def delete_from_library(self, e):
        # Delete audio file in the library
        if os.path.exists(e.audio_path): os.remove(e.audio_path)
        
        # Delete song in the database
        db = DataBase.ConectToDatabase()
        DataBase.DeleteDatabase(db, (e.thumbnail,))
        db.close()

        # Delete song in the library
        self.song_column.controls.remove(e)
        self.song_column.update()

    def build(self):
        self.upload_song_from_database(),
        self.content = Column(
            spacing=0,
            scroll="none",
            horizontal_alignment="center",
            controls=[
                self.AppTitle(),
                self.Heading(),
                Container(
                    width=290,
                    expand=True,
                    content=self.song_column
                )
            ]
        )
        return self.content
    