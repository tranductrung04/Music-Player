from flet import *
from math import pi
import shutil
import os
import re
import requests
import sys
from time import sleep
from ytmusicapi import YTMusic

from data.database import DataBase


class PlayScreen(Container):
    def __init__(self, audio, mini_play, main_stack):
        super().__init__(
            width=290,
            height=600,
            bgcolor= "#9999ff",
            border_radius=border_radius.all(25),
            visible=False,
            # animation
            animate=animation.Animation(duration=500),
            scale=transform.Scale(1, alignment=alignment.bottom_center),
            animate_scale=animation.Animation(duration=500),
        )

        self.mini_play = mini_play
        self.main_stack = main_stack
        self.library_screen = None
        self.lyrics = ""
        self.thumbnail_src = os.getcwd()
        self.title = ""
        self.artist = ""
        self.audio_path = os.getcwd()
        self.audio = audio
        self.current_time = Text(font_family="Roboto-Medium",size=13)
        self.duration = Text(font_family="Roboto-Medium",size=13)

        self.slider = Slider(
            min=0,
            max=0,
            value=0,
            thumb_color="transparent",
            on_change_end=lambda e: self.on_change_slider(round(float(e.data)))
        )

        self.play_pause_icon = self.mini_play.controls[0].content.controls[4]

        self.favorite_icon = IconButton(
            icons.FAVORITE_BORDER_ROUNDED,
            selected_icon=icons.FAVORITE_ROUNDED,
            selected=False,
            selected_icon_color=colors.PINK,
            on_click=lambda e: self.toggle_favorite_icon(e)
        )

        self.thumbnail_container = Container(
            alignment=alignment.center,
            rotate=transform.Rotate(0, alignment=alignment.center),
            animate_rotation=animation.Animation(duration=1000),
            content=CircleAvatar(
                radius=80,
                foreground_image_src=self.thumbnail_src,
            )
        )

        self.audio_changed = False
        self.lyric_timestamp = []
        self.lyric_icon = self.lyricIcon()
        self.time_stamp = self.TimeStamp()
        self.circle_avatar = self.CircleAvatar()
        self.lyric_column = Column(expand=True, scroll=ScrollMode.HIDDEN)
        self.lyric_container = self.lyricContainer()

    def AppBar(self):
        return Container(
            width=290,
            height=50,
            content=Row(
                controls=[
                    IconButton(
                        icons.KEYBOARD_ARROW_DOWN_ROUNDED, 
                        icon_size=30,
                        on_click=lambda e: self.minimize(e)
                    ),
                    Container(width=45),
                    Text("Running...", font_family="Roboto-Medium", size=16)
                ]
            )
        )

    def CircleAvatar(self):
        return Container(
            visible=True,
            width=260,
            height=260,
            content=Stack(
                controls=[
                    Container(
                        gradient=LinearGradient(
                            begin=alignment.top_center,
                            end=alignment.bottom_center,
                            colors=["#333399", "#4d0099"]
                        ),
                        border_radius=500,
                        alignment=alignment.center,
                        content=CircleAvatar(
                            bgcolor="#111827",
                            radius=120,
                        ),
                    ),
                    self.thumbnail_container,
                ]
            )
        )

    def lyricContainer(self):
        return Container(
            visible=False,
            border_radius=10,
            bgcolor="black",
            blur=Blur(10, 0, tile_mode=BlurTileMode.MIRROR),
            width=260,
            height=260,
            content=Stack(
                controls=[
                    Image(
                        width=260,
                        height=260,
                        src=self.thumbnail_src,
                        fit=ImageFit.FILL,
                        opacity=0.5,
                    ),
                    Container(
                        height=260,
                        width=260,
                        padding=10,
                        content=self.lyric_column
                    )
                ]
            )
        )

    def Title(self):
        return Container(
            width=290,
            height=50,
            # bgcolor="purple",
            content=Column(
                spacing=0,
                horizontal_alignment="center",
                controls=[
                    Text(self.title, font_family="Roboto-Medium", no_wrap=True, size=18),
                    Text(self.artist, font_family="Roboto-Medium", no_wrap=True, size=13),
                ]
            )
        )

    def lyricIcon(self):
        return Container(
            content=IconButton(
                icon=icons.LYRICS_OUTLINED,
                selected_icon=icons.LYRICS_ROUNDED,
                selected=False,
                on_click=lambda e: self.toggle_lyric_icon(e)
            )
        )

    def TimeStamp(self):
        return Container(
            width=self.width,
            height=65,
            content=Column(
                spacing=0,
                controls=[
                    self.slider,
                    Row(
                        alignment="spaceBetween",
                        controls=[
                            self.current_time,
                            self.duration,
                        ]
                    )
                ]
            )
        )

    def IconRow(self):
        return Container(
            content=Row(
                alignment=MainAxisAlignment.CENTER,
                controls=[
                    IconButton(
                        icon=icons.REPEAT_ROUNDED, 
                        selected_icon=icons.REPEAT_ONE_ROUNDED,    
                        selected=False,
                        on_click=lambda e: self.toggle_replay_icon(e)
                    ),
                    IconButton(
                        icons.SKIP_PREVIOUS_ROUNDED,
                        on_click=lambda e: self.skip_previous(e),    
                    ),
                    self.play_pause_icon,
                    IconButton(
                        icons.SKIP_NEXT_ROUNDED,
                        on_click=lambda e: self.skip_next(e),    
                    ),
                    self.favorite_icon,
                ]
            )
        )
   
    # Minimize play_screen
    def minimize(self, e):
        self.mini_play.visible = True
        self.mini_play.update()
        self.height = 0
        self.scale = transform.Scale(0.9, alignment=alignment.bottom_center)
        self.update()

    def convert_time_to_ms(self, value: str):
        return 0 if not value else int(60*int(value[0]) + 10*int(value[2]) + int(value[3]))*1000
    
    def format_time(self, value: int):
        ms = value
        tmp = int(ms/1000)
        minute, second = divmod(tmp, 60)
        formatted_time = "{:01}:{:02}".format(int(minute), int(second)) 
        return formatted_time

    def replay(self, state):
        if state=="completed": 
            self.audio.pause()
            self.audio.play()
        
    def no_replay(self):
        pass

    def on_change_slider(self, value):
        self.audio.seek(value)
        self.update_slider_value(value)
        self.update_current_time(value)

    def toggle_lyric_icon(self, e):
        e.control.selected = not e.control.selected
        e.control.update()
        if e.control.selected:
            self.lyric_container.visible = True
            self.circle_avatar.visible = False
        else:
            self.lyric_container.visible = False
            self.circle_avatar.visible = True
        self.update()
        self.main_stack.update()

    def toggle_play_pause_icon(self, e):
        e.control.selected = not e.control.selected
        e.control.update()
        self.audio.pause() if e.control.selected else self.audio.resume()
        self.audio.update()

    def toggle_replay_icon(self, e):
        e.control.selected = not e.control.selected
        e.control.update()
        if e.control.selected: 
            self.audio.on_state_changed = lambda e: self.replay(e.data) 
        else:
            self.no_replay()

    def toggle_favorite_icon(self, e):
        e.control.selected = not e.control.selected
        e.control.update()

        # Change audio src to mylibrary
        self.audio_path = os.path.join(os.getcwd(), "assets", "mylibrary", re.split(r"\\|/", self.audio_path)[-1])
        # print(self.audio_path)

        self.add_to_library() if e.control.selected else self.delete_from_library()

    def rotate_thumnail(self):
        self.thumbnail_container.rotate.angle += pi/10
        self.thumbnail_container.update()

    def add_to_library(self):
        # Copy audio file to folder mylibrary 
        src = os.path.join(os.getcwd(), "assets", "mymusic", re.split(r"\\|/", self.audio_path)[-1])
        dst = "assets/mylibrary"
        shutil.copy(src, dst)

        # Connect and insert song to the database
        db = DataBase.ConectToDatabase()
        DataBase.InsertDatabase(db, (self.audio_path, self.thumbnail_src, self.title, self.artist, self.duration.value, self.lyrics,))
        # for record in DataBase.ReadDatabase(db):
        #     print(record) 
        db.close()

        # Append song to library
        self.library_screen.song_column.controls.append(
            Song(self.audio_path, self.thumbnail_src, self.title, self.artist, self.duration.value, self.lyrics, self, self.main_stack), 
        )
        self.library_screen.song_column.update()

    def delete_from_library(self):
        lib = self.library_screen.song_column.controls
        for song in lib:
            if self.thumbnail_src == song.content.content.controls[0].src:
                self.library_screen.delete_from_library(song)
                break
    
    def skip_previous(self, e):
        # Exception: there is only one song in library
        db = DataBase.ConectToDatabase()
        songs = DataBase.ReadDatabase(db)
        for i in range(len(songs)):
            if songs[i][1] == self.thumbnail_src:
                if i == 0:
                    Song(songs[-1][0], songs[-1][1], songs[-1][2], songs[-1][3], songs[-1][4], songs[-1][5], self, self.main_stack).play_music()
                    break
                else: 
                    Song(songs[i-1][0], songs[i-1][1], songs[i-1][2], songs[i-1][3], songs[i-1][4], songs[i-1][5], self, self.main_stack).play_music()
                    break
        else:
            Song(songs[-1][0], songs[-1][1], songs[-1][2], songs[-1][3], songs[-1][4], songs[-1][5], self, self.main_stack).play_music()
        db.close()

    def skip_next(self, e):
        # Exception: there is only one song in library
        db = DataBase.ConectToDatabase()
        songs = DataBase.ReadDatabase(db)
        for i in range(len(songs)):
            if songs[i][1] == self.thumbnail_src:
                if i == len(songs)-1:
                    Song(songs[0][0], songs[0][1], songs[0][2], songs[0][3], songs[0][4], songs[0][5], self, self.main_stack).play_music()
                    break
                else: 
                    Song(songs[i+1][0], songs[i+1][1], songs[i+1][2], songs[i+1][3], songs[i+1][4], songs[i+1][5], self, self.main_stack).play_music()
                    break
        else:
            Song(songs[0][0], songs[0][1], songs[0][2], songs[0][3], songs[0][4], songs[0][5], self, self.main_stack).play_music()
        db.close()

    def update_favorite_icon(self):
        db = DataBase.ConectToDatabase()
        for item in DataBase.ReadDatabase(db):
            if item[1] == self.thumbnail_src:
                self.favorite_icon.selected = True
                break
        db.close()

    def update_mini_play(self):
        self.mini_play.controls[0].content.controls[0].src = self.thumbnail_src
        self.mini_play.controls[0].content.controls[2].content.controls[0].value = self.title
        self.mini_play.controls[0].content.controls[2].content.controls[1].value = self.artist
    
    def update_image_and_lyric(self):
        self.thumbnail_container.content.foreground_image_src = self.thumbnail_src
        self.lyric_container.content.controls[0].src = self.thumbnail_src
        
        self.lyric_timestamp.clear()
        self.lyric_column.controls.clear()

        try:
            # Send a GET request to the URL
            response = requests.get(self.lyrics).json()
            lyrics = response["lyrics"]

            self.lyric_timestamp = lyrics

            # Update lyric_column and lyric_timestamp
            for lyric in lyrics:
                self.lyric_column.controls.append(
                    Container(
                        content=Text(value=lyric["words"], font_family="Roboto-Medium", size=14, color=colors.WHITE54),
                        key=lyric["startTimeMs"],
                        on_click=lambda e: self.on_change_slider(int(e.control.key))
                    )
                )

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")

    def getCurrentLine(self):
        nextIdx = 0
        if self.audio_changed == True: sys.exit(0)
        get_current_position = self.audio.get_current_position()

        for x in self.lyric_timestamp:
            try:
                if int(x["startTimeMs"]) > get_current_position:
                    nextIdx = self.lyric_timestamp.index(x)
                    break

            except Exception as e:
                print(f"getCurrentLine: {e}")
                sys.exit(0)

        if nextIdx == 0: return 0
        currentIdx = nextIdx - 1
        return currentIdx

    def sync_lyric(self, idx):
        # Highlight text
        self.lyric_column.controls[idx].content.color = colors.WHITE
        if idx!=0: self.lyric_column.controls[idx-1].content.color = colors.WHITE54
        self.update()

        # Scroll
        self.lyric_column.scroll_to(key=self.lyric_timestamp[idx]["startTimeMs"], duration=1000)

    def on_scroll_lyric(self, state):
        try:
            while not self.play_pause_icon.selected:
                if self.audio_changed == True: sys.exit(0)
                idx = self.getCurrentLine()
                sleep(0.1)
                print(idx)
                self.sync_lyric(idx)

        except Exception as e:
            print(f"on_scroll_lyric: {e}")

    def update_audio(self):
        self.audio.src = self.audio_path
        self.audio_changed = True
        self.audio.autoplay = True
        self.slider.value = 0
        self.audio.on_position_changed = lambda e: self.update_timestamp(int(e.data))
        self.slider.max = 0 if not self.duration.value else self.convert_time_to_ms(self.duration.value)
        self.audio.on_state_changed = lambda e: self.on_scroll_lyric(e.data)
        self.audio_changed = False
        
    def update_timestamp(self, value):
        if value != 0 and value%1000 == 0: 
            self.rotate_thumnail()
            self.update_slider_value(value)
            self.update_current_time(value)

    def update_current_time(self, value):
        self.current_time.value = self.format_time(value)
        self.current_time.update()

    def update_slider_value(self, value):
        self.slider.value = value
        self.slider.update()

    def build(self):
        self.library_screen = self.main_stack.controls[0].controls[0].content.controls[2]
        self.update_favorite_icon()
        self.update_audio()
        self.update_image_and_lyric()
        self.update_mini_play()
        self.content=Column(
            spacing=0,
            controls=[
                self.audio,
                self.AppBar(),
                Container(
                    expand=True,
                    padding=padding.only(left=15, right=15, bottom=15),
                    content=Column(
                        horizontal_alignment="center",
                        spacing=0,
                        controls = [
                            Divider(height=30, color="transparent"),
                            Stack(
                                # scroll=ScrollMode.ADAPTIVE,
                                controls=[
                                    self.circle_avatar,
                                    self.lyric_container,
                                ]
                            ),
                            Divider(height=20, color="transparent"),
                            self.Title(),
                            self.lyric_icon,
                            self.time_stamp,
                            self.IconRow(),
                        ]
                    )
                )
            ]
        )
        return self.content


class Song(Container):
    def __init__(self, audio_path, thumbnail, title, artist, duration, lyrics, play_screen, main_stack):
        super().__init__()
        self.play_screen = play_screen
        self.main_stack = main_stack
        self.audio_path = audio_path
        self.thumbnail = thumbnail
        self.title = title
        self.artist = artist
        self.duration = duration
        self.lyrics = lyrics

    def play_music(self):
        # Delete old audio file in mymusic
        # path = os.path.join(os.getcwd(),"assets", "mymusic")
        # for file in os.listdir(path):
        #     os.remove(os.path.join(path,file))
        # print("Cleaned mymusic")

        # Remove the old audio and play_screen
        while len(self.main_stack.controls) > 1:
            self.main_stack.controls.pop(-1)
        self.main_stack.update()

        # Assign values in the database to the attributes of play_screen
        db = DataBase.ConectToDatabase()
        for item in DataBase.ReadDatabase(db):
            if item[1] == self.thumbnail:
                self.audio_path = item[0]
                self.thumbnail = item[1]
                self.title = item[2]
                self.artist = item[3]
                self.duration = item[4]
                self.lyric = item[5]
                break
        db.close()
        
        # Update the audio and play_screen
        self.play_screen.audio = Audio(src=self.audio_path, autoplay=False)
        self.play_screen.audio_path = self.audio_path
        self.play_screen.thumbnail_src = self.thumbnail
        self.play_screen.title = self.title
        self.play_screen.artist = self.artist
        self.play_screen.duration.value = self.duration
        self.play_screen.lyrics = self.lyrics
        self.play_screen.favorite_icon.selected = False
        self.play_screen.play_pause_icon.selected = False 
        self.play_screen.lyric_icon.selected = False

        # Update the mini_play
        self.main_stack.controls[0].controls[0].content.controls[3].controls[0].content.controls[4].on_click = self.play_screen.toggle_play_pause_icon
        self.play_screen.update_mini_play()
        self.main_stack.update()

        # Appending the audio and play_screen
        self.main_stack.controls.append(self.play_screen.audio)
        self.main_stack.controls.append(
            Column(
                alignment = "end",
                controls=[
                    self.play_screen
                ]
            )
        )
        self.play_screen.visible = True
        self.main_stack.update()

    def build(self):
        self.content = Container(
            on_click=lambda _: self.play_music(),
            bgcolor="#c1d0f0",
            width=290,
            height=50,
            border_radius=10,
            content=Row(
                spacing=0,
                controls=[
                    Image(
                        border_radius=10,
                        width=50,
                        height=50,
                        fit=ImageFit.FILL,
                        src=self.thumbnail,
                    ),
                    Container(width=10),
                    Container(
                        width=150,
                        content=Column(
                            spacing=1,
                            controls=[
                                Text(self.title, font_family="Roboto-Medium",no_wrap=True),
                                Text(self.artist, font_family="Roboto-Medium", size=13, opacity=0.8, no_wrap=True),
                            ]
                        )
                    ),
                    Container(width=20),
                    IconButton(
                        icon=icons.DELETE,
                        on_click=lambda e: self.main_stack.controls[0].controls[0].content.controls[2].delete_from_library(self),
                    )
                ]
            )
        )
        return self.content
        