import re
from flet import *
import os
from time import sleep
from datetime import datetime
from urllib.parse import quote
from ytmusicapi import YTMusic
from pytubefix import YouTube
import assemblyai as aai

from views.playscreen import *


class SearchScreen(Container):
    def __init__(self, play_container, main_stack, audio):
        super().__init__(
            width=290,
            height=560,
            border_radius=border_radius.only(top_left=25, top_right=25), 
            visible=False,
        )

        self.play_container = play_container
        self.main_stack = main_stack
        self.audio = audio

        self.audio_rec = AudioRecorder(
            audio_encoder=AudioEncoder.WAV,
            suppress_noise=True,
            cancel_echo=True,
            on_state_changed=lambda e: self.handle_record_change(e),
        )

        self.search_result = Column(spacing=0)
        self.search_bar = self._SearchBar()
        self.progress_bar = self._ProgressBar()
        self.error_search_container = self.ErrorSearchContainer()
        self.suggestion_res = self.SuggestionContainer()
        self.voice_container = self.VoiceContainer()

    def _ProgressBar(self):
        return ProgressBar(
            width=self.width-30,
            color="red",
            bar_height=3,
            visible=False,
        )

    def ErrorSearchContainer(self):
        return Container(
            padding=padding.only(top=20),
            visible=False,
            expand=True,
            content=Column(
                spacing=1,
                horizontal_alignment="center",
                controls=[
                    Image(height=150, width=150, src="assets/images/search-result-find-illustration_585024-17-removebg-preview.png", fit=ImageFit.COVER),
                    Text("Opps, there was no matching results!", font_family="Roboto-Medium", size=15, italic=True),
                ]
            )
        )

    def _SearchBar(self):
        return Container(
            padding=padding.only(top=15, left=15, right=15),
            content=Container(
                width=self.width,
                height=40,
                border_radius=30,
                padding=padding.only(left=10),
                bgcolor="#e6e6e6",
                content=Row(
                    spacing=0,
                    vertical_alignment="center",
                    controls=[
                        Icon(icons.SEARCH_ROUNDED, size=20, opacity=0.8),
                        Container(width=10),
                        TextField(
                            expand=True,
                            hint_text=Text("Search...", font_family="Roboto-Medium", opacity=0.8, size=15).value, 
                            border_color="transparent",
                            height=20,
                            opacity=0.8, 
                            text_size=15,
                            text_style=TextStyle(font_family="Roboto-Medium"), 
                            content_padding=2,
                            autofocus=True,
                            on_change=lambda e: self.on_change_search(e),
                            on_submit=lambda e: self.SearchSong(e.control.value),
                        ),
                        IconButton(icon=icons.MIC_ROUNDED, icon_size=20, opacity=0.8, on_click=lambda e: self.voice_search(e)),
                    ]
                )
            )
        )

    def SuggestionContainer(self):
        return Container(
            width=self.width,
            border_radius=20,
            bgcolor="#e6e6e6",
            content=Column(scroll="auto")
        )

    def VoiceContainer(self):
        return Container(
            width=self.width,
            bgcolor="#e6e6e6",
            border_radius=15,
            visible=False,
            padding=padding.only(bottom=10, left=10, right=10),
            expand=True,
            content=Column(
                spacing=0,
                horizontal_alignment="center",
                controls=[
                    self.audio_rec,
                    Row(
                        alignment=MainAxisAlignment.END,
                        controls=[IconButton(icon=icons.CLOSE_ROUNDED, icon_size=25, on_click=lambda e: self.close_voice_search(e))]
                    ),
                    Row(
                        alignment="center",
                        vertical_alignment="center", 
                        controls=[ProgressRing(height=25, width=25, visible=False), Text("Say something...", font_family="Roboto-Medium", size=16)]
                    ),
                    IconButton(icon=icons.MIC_ROUNDED, icon_size=50, icon_color="pink", selected=False, disabled=True, opacity=0.8, on_click=lambda e: self.voice_search(e)),
                    Text("", font_family="Roboto-Medium", size=14),
                ]
            )
        )

    def on_change_search(self, e):
        self.suggestion_res.content.controls.clear()
        self.update()
        search_suggestion_res = YTMusic().get_search_suggestions(query=e.control.value)
        for item in search_suggestion_res:
            self.suggestion_res.content.controls.append(
                Container(
                    padding=padding.only(left=15, right=15),
                    content=Text(item, size=14, font_family="Roboto-Medium", italic=True),
                    on_click=lambda e: self.SearchSong(e.control.content.value),
                )
            )
        self.suggestion_res.visible = True
        self.update()

    def handle_record_change(self, e):
        print(f"State Changed: {e.data}")

    def close_voice_search(self, e):
        self.voice_container.visible = False
        self.voice_container.content.controls[-1].value = ""
        self.voice_container.content.controls[2].controls[1].value = "Say something..."
        self.update()

    def voice_search(self, e):
        self.voice_container.content.controls[2].controls[1].value = "Say something..."
        self.voice_container.content.controls[2].controls[0].visible = False
        self.voice_container.content.controls[3].icon_color = "pink"
        self.voice_container.content.controls[3].disabled = True
        self.voice_container.content.controls[-1].value = ""
        self.voice_container.visible = True
        self.update()

        path = "assets/records/record-file.wav"
        try:
            print(f"HasPermission: { self.audio_rec.has_permission(wait_timeout=0.1)}")
        except Exception as e:
            print(e)

        self.audio_rec.start_recording(path)
        sleep(6)
        self.audio_rec.stop_recording()
        self.voice_container.content.controls[2].controls[0].visible = True
        self.voice_container.content.controls[2].controls[1].value = "OK, just a moment..."
        self.update()

        aai.settings.api_key = "019bc02127824606bf15c0c5183c9011"
        config = aai.TranscriptionConfig(language_detection=True)

        transcript = aai.Transcriber().transcribe(path, config)

        self.voice_container.content.controls[2].controls[0].visible = False

        if transcript.status == aai.TranscriptStatus.error or transcript.text == "":
            print(transcript.error)
            self.voice_container.content.controls[2].controls[1].value = "I haven't heard clearly yet"
            self.voice_container.content.controls[3].icon_color = None
            self.voice_container.content.controls[3].disabled = False
            self.voice_container.content.controls[-1].value = "Click the microphone to try again"
            self.update()

        else:
            print(transcript.text)
            self.voice_container.content.controls[2].controls[1].value = "Searching..."
            for char in transcript.text:
                self.voice_container.content.controls[-1].value += char
                self.update()
                sleep(0.05)

            # Delay before searching
            sleep(3)

            self.search_bar.content.content.controls[2].value = self.voice_container.content.controls[-1].value
            self.SearchSong(self.voice_container.content.controls[-1].value)

    def SearchSong(self, value):
        # Clear search_screen
        self.voice_container.visible = False
        self.suggestion_res.visible = False
        self.suggestion_res.content.controls.clear()
        self.suggestion_res.content.update()
        self.search_result.controls.clear()
        self.search_result.update()
        self.update()

        if not value:
            print("Error Search")
            self.error_search_container.visible = True
        else:
            self.error_search_container.visible = False

            # Calling API
            result = YTMusic().search(query=value, filter="songs")

            if result:
                for x in result:
                    self.search_result.controls.append(
                        ListTile(
							leading=Image(
								src=x['thumbnails'][0]['url'] if len(x['thumbnails'])==1 else x['thumbnails'][1]['url'],
								fit="fill",
								width=120,
								height=120,
								border_radius=10
							),
							title=Column([
								Text(x['title'],font_family="Roboto-Bold", size=14, max_lines=2),
								Text(x['duration'], font_family="Roboto-Medium", size=10),
								Text(x['artists'][0]['name'] if x["artists"] else "Unknown", font_family="Roboto-Medium", size=12),
							], spacing=1),
							subtitle=Text(x['videoId'], font_family="Roboto-Medium", size=10, visible=False),
							on_click=lambda e: self.PlayMusic(e),
						)
                    )
            else:
                print("Error Search")
                self.error_search_container.visible = True
        self.update()

    def PlayMusic(self, e):
        print("Clicked")

        # Delete old audio file in mymusic
        path = os.path.join(os.getcwd(),"assets", "mymusic")
        for file in os.listdir(path):
            os.remove(os.path.join(path,file))
        print("Cleaned mymusic")

        # Enable the progress_bar
        self.progress_bar.visible = True
        self.progress_bar.update()

        # Download the audio from youtube
        videoId = e.control.subtitle.value
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
        self.play_container.controls[0].thumbnail_src = e.control.leading.src
        self.play_container.controls[0].title = e.control.title.controls[0].value
        self.play_container.controls[0].artist = e.control.title.controls[2].value
        self.play_container.controls[0].duration.value = e.control.title.controls[1].value
        self.play_container.controls[0].audio_path = audio_path
        self.play_container.controls[0].favorite_icon.selected = False
        self.play_container.controls[0].play_pause_icon.selected = False
        self.play_container.controls[0].lyric_icon.selected = False
       
        # Update the lyrics
        song_title = self.play_container.controls[0].title
        encoded_text = quote(song_title)

        # URL of the JSON data
        url = f"https://lyrics-api.boidu.dev/getLyrics?s={encoded_text}"

        self.play_container.controls[0].lyrics = url

        # Get lyrics from ytmusicapi
        # watch_res = YTMusic().get_watch_playlist(videoId=videoId)
        # browserLyricId = "" if not watch_res["lyrics"] else watch_res["lyrics"]
        # if browserLyricId != "": 
        #     lyric_res = YTMusic().get_lyrics(browseId=browserLyricId)
        #     # print(lyric_res["lyrics"]) 
        #     self.play_container.controls[0].lyric = lyric_res["lyrics"]
        # else: self.play_container.controls[0].lyric = "Opps, something went wrong!"

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

            # Disable the progress_bar
            self.progress_bar.visible = False
            self.progress_bar.update()

            # Enable the PlayScreen
            self.play_container.controls[0].visible = True
            self.play_container.controls[0].update()
            self.main_stack.update()

    def build(self):
        self.content = Stack(
            controls=[
                # Image(src="assets/images/fishingrobot.jfif", fit=ImageFit.COVER, width=self.width, height=self.height),
                Column(
                    scroll="none",
                    horizontal_alignment="center",
                    spacing=0,
                    controls=[
                        self.search_bar,
                        Divider(height=5, color="transparent"),
                        self.progress_bar,
                        Divider(height=5, color="transparent"),
                        Container(
                            expand=True,
                            padding=padding.only(left=15, right=15),
                            content=Column(
                                scroll="hidden",
                                spacing=0,
                                controls=[
                                    Stack(
                                        controls=[
                                            self.error_search_container,
                                            self.search_result,
                                            self.suggestion_res,
                                            self.voice_container,
                                        ]
                                    )
                                ]
                            )
                        )
                    ]
                )
            ]
        )
        return self.content
    