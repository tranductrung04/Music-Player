from flet import *
from fletcarousel import *
import os
import re
from datetime import datetime
from urllib.parse import quote
import requests
from ytmusicapi import YTMusic
from pytubefix import YouTube


class HomeScreen(Container):
    def __init__(self, search_screen, play_container, main_stack):
        super().__init__(
            width=290,
            height=560,
            border_radius=border_radius.only(top_left=25, top_right=25),
            padding=padding.only(left=10),    
            visible=True,
        )
        self.play_container = play_container
        self.main_stack = main_stack
        self.search_screen = search_screen
        self.progress_bar = self._ProgressBar()
        self.quick_picks = self.QuickPicks()
        self.albums_for_you =self.AlbumsForYou()

    def GetContainerColor(self, container_name:str):
        colors_lookup = [
            colors.AMBER,
            colors.GREEN,
            colors.INDIGO,
            colors.LIME,
            colors.GREEN_ACCENT,
            colors.ORANGE,
            colors.PURPLE,
            colors.RED,
            colors.YELLOW,
            colors.DEEP_ORANGE,
        ]
        return colors_lookup[hash(container_name)%len(colors_lookup)]

    def AppTitle(self):
        return Container(
            height=60,
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

    def _ProgressBar(self):
        return ProgressBar(
            width=self.width-30,
            color="red",
            bar_height=3,
            visible=False,
        )

    def ChangeThemeIcon(self):
        return IconButton(
            icon=icons.DARK_MODE_ROUNDED,
            selected_icon=icons.SUNNY,
            selected=False,
            on_click=lambda e: self.toggle_theme_mode(e)
        )
    
    def toggle_theme_mode(self, e):
        e.control.selected = not e.control.selected
        e.control.update()
        e.page.theme_mode = "dark" if e.control.selected==True else "light"

    def CarouselAutomaticSlider(self):
        # Create a dict of images
        images = {
            "assets/images/bainaychillphet.jpg",
            "assets/images/buonHayVui.jpg",
            "assets/images/cohenvoithanhxuan.jpg",
            "assets/images/dunglamtraitimanhdau.jpg",
            "assets/images/muonroimasaocon.jpg",
            "assets/images/noinaycoanh.jpg",
            "assets/images/thangdien.jpg",
            "assets/images/xichthemchut.jpg",
        }
        return BasicAnimatedHorizontalCarousel(
            page=self.page,
            auto_cycle=AutoCycle(duration=2),
            animated_switcher=AnimatedSwitcher(
                transition=AnimatedSwitcherTransition.SCALE,
                duration=1000,
                reverse_duration=100,
                switch_in_curve=AnimationCurve.FAST_OUT_SLOWIN,
                switch_out_curve=AnimationCurve.FAST_OUT_SLOWIN,
                content=Control(),
            ),
            hint_lines=HintLine(
                active_color="blue",
                inactive_color=colors.GREY_300 if self.page.theme_mode=="light" else colors.WHITE10,
                alignment="center",
                max_list_size=100,
            ),
            items=[
                Row(
                    vertical_alignment="center",
                    controls=[
                        Image(
                            width=200,
                            height=100,
                            border_radius=15,
                            expand=True,
                            src=i,
                            fit="cover",
                        )
                    ]
                )for i in images
            ]
        )

    def GenresRow(self):
        # API calling
        categories_res = YTMusic().get_mood_categories()

        # Creating a row of Genres['title']
        self.genres_list = Row(
            expand=True,
            scroll=ScrollMode.AUTO,
            controls=[
                Column(
                    horizontal_alignment="center",
                    controls=[Container(
                        width=60,
                        height=50,
                        border_radius=12,
                        bgcolor=colors.PINK,
                        padding=padding.only(top=5, bottom=5),
                        content=Column(
                            horizontal_alignment="center",
                            spacing=1,
                            controls=[
                                Text("Genres", font_family="Roboto-Medium"),
                                Icon(icons.LIBRARY_MUSIC_OUTLINED, size=17)
                            ]
                        )
                    )]
                )
            ]
        ) 
        
        for genres in categories_res['Genres']:
            self.genres_list.controls.append(
                Column(
                    horizontal_alignment="center",
                    controls=[Container(
                        width=130,  
                        height=50,
                        border_radius=12,
                        padding=padding.only(top=10, bottom=10),
                        bgcolor=self.GetContainerColor(genres['title']),
                        content=Column(
                            horizontal_alignment="center",
                            controls=[
                                Text(genres['title'], font_family="Roboto-Medium", no_wrap=True)
                            ]
                        )
                    )]
                )
            )
        return self.genres_list
    
    def MoodsRow(self):
        # API calling
        categories_res = YTMusic().get_mood_categories()

        # Creating a row of Genres['title']
        self.moods_list = Row(
            expand=True,
            scroll=ScrollMode.AUTO,
            controls=[
                 Container(
                    width=60,
                    height=50,
                    border_radius=12,
                    bgcolor=colors.PINK,
                    padding=padding.only(top=5, bottom=5),
                    content=Column(
                        horizontal_alignment="center",
                        spacing=1,
                        controls=[
                            Text("Moods", font_family="Roboto-Medium"),
                            Icon(icons.EMOJI_EMOTIONS_OUTLINED, size=17)
                        ]
                    )
                )
            ]
        ) 
        
        for moods in categories_res['Moods & moments']:
            self.moods_list.controls.append(
                Container(
                    width=130,  
                    height=50,
                    border_radius=12,
                    padding=padding.only(top=10, bottom=10),
                    bgcolor=self.GetContainerColor(moods['title']),
                    content=Column(
                        horizontal_alignment="center",
                        controls=[
                            Text(moods['title'], font_family="Roboto-Medium", no_wrap=True)
                        ]
                    )
                )
            )
        return self.moods_list

    def ChartsRow(self):
        countries = {"US": "US", "GB":"GB", "JP":"JP", "KR":"KR", "NG":"NG"}

        # Creating a row of Charts
        self.charts_list = Row(expand=True, scroll=ScrollMode.AUTO) 
        
        for country in countries:
            # API calling
            charts_res = YTMusic().get_charts(country)['videos']['items']
            country_name = YTMusic().get_charts(country)['countries']['selected']['text']

            self.charts_column = Column()
            for i in range(5):
                self.charts_column.controls.append(
                    Row(
                        spacing=5,
                        controls=[
                            Container(
                                width=40,
                                height=40,
                                border_radius=10,
                                content=Image(
                                    fit="fill",
                                    src=charts_res[i]['thumbnails'][0]['url'],
                                )
                            ),
                            Column(
                                spacing=1,
                                controls=[
                                    Text(f"{i+1}. {charts_res[i]['title']}", font_family="Roboto-Medium", size=13, no_wrap=True),
                                    Text(f"    {charts_res[i]['artists'][0]['name']}", font_family="Roboto-Medium", size=10, opacity=0.8, no_wrap=True),
                                ]
                            )
                        ]
                    )
                )

            self.charts_list.controls.append(
                Container(
                    width=200,  
                    height=285,
                    border_radius=12,
                    bgcolor="#c1d0f0" if self.page.theme_mode=="light" else colors.WHITE10,
                    padding=padding.all(5),
                    content=Column(
                        controls=[
                            Text(country_name, font_family="Roboto-Bold"),
                            self.charts_column,
                        ]
                    )
                )
            )

        return self.charts_list        

    def QuickPicks(self):
        res = YTMusic().get_home()
        # len(res)=2
        # res[0]: quickPicks
        # res[1]: albumsForYou

        quickPickList = Row(expand=True, scroll=ScrollMode.AUTO)
        for x in res[0]["contents"]:
            quickPickList.controls.append(
                Container(
                    padding=padding.only(top=10, bottom=10),
                    on_click=lambda e: self.PlayMusic(e.control.content.controls[-1].value, e.control.content.controls[0].src, e.control.content.controls[2].value, e.control.content.controls[-2].value),
                    content=Column(
                        spacing=0,
                        controls=[
                            Image(
                                width=100,
                                height=100,
                                border_radius=15,
                                src=x["thumbnails"][1]["url"] if "thumbnails" in x and len(x["thumbnails"])>1 else x["thumbnails"][0]["url"],
                                fit=ImageFit.FILL,
                            ),
                            Container(height=2),
                            Text(value=x["title"], font_family="Roboto-Bold", size=12, width=100, max_lines=2),
                            Text(value=x["artists"][0]["name"] if "artists" in x and x["artists"] else "Unknown", font_family="Roboto-Medium", size=11, opacity=0.9, width=100, max_lines=2),
                            Text(value=x["videoId"], visible=False)
                        ]
                    )
                )
            )

        return Column(
            spacing=0,
            controls=[
                Text(res[0]["title"], font_family="Roboto-Bold", size=16),
                quickPickList,
            ]
        )

    def AlbumsForYou(self):
        res = YTMusic().get_home()

        albumList = Row(expand=True, scroll=ScrollMode.AUTO)
        for x in res[1]["contents"]:
            albumList.controls.append(
                Container(
                    padding=padding.only(top=10, bottom=10),
                    content=Column(
                        spacing=0,
                        controls=[
                            Image(
                                width=100,
                                height=100,
                                border_radius=15,
                                src=x["thumbnails"][1]["url"] if "thumbnails" in x and len(x["thumbnails"])>1 else x["thumbnails"][0]["url"],
                                fit=ImageFit.FILL,
                            ),
                            Container(height=2),
                            Text(value=x["title"], font_family="Roboto-Bold", size=12, width=100, max_lines=2),
                            Text(value=x["artists"][0]["name"] if "artists" in x and x["artists"] else "Unknown", font_family="Roboto-Medium", size=11, opacity=0.9, width=100, max_lines=2),
                        ]
                    )
                )
            )

        return Column(
            spacing=0,
            controls=[
                Text(res[1]["title"], font_family="Roboto-Bold", size=16),
                albumList,
            ]
        )

    def ms_to_minutes(self, ms):
        # Convert milliseconds to total seconds
        total_seconds = ms // 1000
        
        # Get minutes and remaining seconds
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        # Format minutes and seconds with leading zeroes if needed
        return f"{minutes}:{seconds:02}"

    def PlayMusic(self, videoId, thumbnail, title, artist):
        print("Clicked")

        # Enable ProgressBar
        self.progress_bar.visible = True
        self.update()

        # Download the audio from youtube
        videoUrl = f"https://youtube.com/watch?v={videoId}"
        yt = YouTube(videoUrl)
        stream = yt.streams.filter(only_audio=True)
        audio_path = stream.get_audio_only().download(output_path="assets/mymusic")
        
        # Unique file audio name
        root_path = os.path.join(os.getcwd(), "assets", "mymusic")
        file_name = re.split(r"\\|/", audio_path)[-1].split(".")
        unique_filename = file_name[0] + " " + datetime.now().strftime('%Y-%m-%d %H-%M-%S') + "." + file_name[1]
        dst = f"{root_path}\\{unique_filename}"
        os.rename(audio_path, dst)
        audio_path = dst

        # Remove the old audio and play_screen
        while len(self.main_stack.controls) > 1:
            self.main_stack.controls.pop(-1)
        self.main_stack.update()

        # Update the audio and the play_screen
        self.play_container.controls[0].audio = Audio(src=audio_path, autoplay=False)
        self.play_container.controls[0].thumbnail_src = thumbnail
        self.play_container.controls[0].title = title
        self.play_container.controls[0].artist = artist
        self.play_container.controls[0].duration.value = ""
        self.play_container.controls[0].audio_path = audio_path
        self.play_container.controls[0].favorite_icon.selected = False
        self.play_container.controls[0].play_pause_icon.selected = False
        self.play_container.controls[0].lyric_icon.selected = False
       
        # Update the lyrics
        encoded_text = quote(title)

        # URL of the JSON data
        url = f"https://lyrics-api.boidu.dev/getLyrics?s={encoded_text}"
        self.play_container.controls[0].lyrics = url

        try:
            response = requests.get(url).json()
            lyrics = response["lyrics"]
            
            self.play_container.controls[0].duration.value = str(self.ms_to_minutes(int(lyrics[-1]["startTimeMs"])))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")

        # Update the mini_play
        self.main_stack.controls[0].controls[0].content.controls[3].controls[0].content.controls[4].on_click = self.play_container.controls[0].toggle_play_pause_icon
        self.play_container.controls[0].update_mini_play()
        self.main_stack.update()

        # Appending the audio and the play_screen
        self.main_stack.controls.append(self.play_container.controls[0].audio)
        self.main_stack.controls.append(self.play_container)
        self.main_stack.update()

        # Play music
        if not audio_path == "":
            print("Your download is finished!")

            # Disable ProgressBar
            self.progress_bar.visible = False
            self.update()

            # Enable the PlayScreen
            self.play_container.controls[0].visible = True
            self.play_container.controls[0].update()
            self.main_stack.update()

    def build(self):
        self.content = Column(
            scroll="none",
            horizontal_alignment="center",
            spacing=0,
            controls=[
                Container(
                    padding=padding.only(right=15),
                    content=Row(
                        alignment="spaceBetween",
                        controls=[
                            self.AppTitle(),
                            # self.ChangeThemeIcon(),
                        ]
                    )
                ),
                self.progress_bar,
                Container(
                    expand=True,
                    content=Column(
                        horizontal_alignment="center",
                        scroll=ScrollMode.HIDDEN,
                        controls=[
                            Container(
                                width=200,
                                height=120,
                                padding=padding.only(bottom=20),
                                content=self.CarouselAutomaticSlider(),
                            ),
                            Container(
                                height=50,
                                content=Column(
                                    controls=[
                                        self.GenresRow(),
                                    ]
                                )
                            ),
                            Container(
                                content=Column(
                                    controls=[
                                        self.MoodsRow(),
                                    ]
                                )
                            ),
                            Container(
                                content=Column(
                                    controls=[
                                        Text("Charts", font_family="Roboto-Bold", size=16),
                                        self.ChartsRow(),
                                    ]
                                )
                            ),
                            self.quick_picks,
                            self.albums_for_you,
                            Container(height=30),
                            Divider(height=10, color=colors.WHITE10),
                        ],
                    )
                ),
            ]
        )
        return self.content
    