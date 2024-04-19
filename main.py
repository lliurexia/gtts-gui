"""
flet repository: https://github.com/flet-dev/flet
flet docs: https://flet.dev/

gtts repository: https://github.com/pndurette/gTTS
gtts docs: https://gtts.readthedocs.io/en/latest/
"""

# default.
from pathlib import Path
from shutil import copyfile
from traceback import print_exc
from typing import Callable
from typing import List
from typing import Optional

# 3rd.
import flet as ft
import gtts.lang
from gtts import gTTS


class Constructor:
    def __init__(self, application: 'Application') -> None:
        self.application = application

        # binding.
        self.application.start_tts_button.on_click = self.handle_start_speech_generation
        self.application.play_button.on_click = self.handle_play_audio
        self.application.pause_button.on_click = self.handle_pause_audio
        self.application.save_button.on_click = self.handle_save_audio
        self.application.appbar.toggle_theme_button.on_click = self.handle_toggle_theme_mode

        # setting languages.
        langs = (list(gtts.lang.tts_langs().keys()))
        self.application.set_lang_options(langs)
        self.application.set_lang('en')

        # setting Top-level domains.
        with open('supported_domains.txt') as file:
            domains = [domain.split('google.')[-1] for domain in file.read().split(' ')]
            domains.sort()
        
        self.application.set_domain_options(domains)
        self.application.set_domain('com')

    def handle_play_audio(self, _event: ft.ControlEvent) -> None:
        self.application.play_audio()

    def handle_pause_audio(self, _event: ft.ControlEvent) -> None:
        self.application.pause_audio()

    def handle_save_audio(self, _event: ft.ControlEvent) -> None:
        self.application.open_save_file(on_result=self.handle_file_picker_on_result)

    def handle_toggle_theme_mode(self, _event: ft.ControlEvent) -> None:
        self.application.toggle_theme_mode()
        
    def handle_start_speech_generation(self, _event: ft.ControlEvent) -> None:
        try:
            lang = self.application.get_lang()
            tld = self.application.get_domain()
            text = self.application.get_input()
            cache_directory = Path('.cache')
            temp_file_path = cache_directory / 'audio.mp3'

            self.application.start_progress_ring()
            self.application.hide_audio_controllers()
            self.application.close_banner()
            self.application.clear_input_error_text()

            if not len(text.strip()):
                self.application.show_input_error_text('Required.')
                self.application.focus_input_field()
                return

            if not cache_directory.exists():
                cache_directory.mkdir()
            
            tts = gTTS(text, lang=lang, tld=tld)
            tts.save(temp_file_path)

            self.application.set_audio_source(str(temp_file_path.absolute()))
            self.application.show_audio_controllers()

        except Exception as error:
            print_exc()
            self.application.show_danger_banner(str(error))

        finally:
            self.application.stop_progress_ring()

    def handle_file_picker_on_result(self, event: ft.FilePickerResultEvent) -> None:
        if event.path is None:
            print('Output path not defined.')
            return
        
        elif self.application.get_audio_source() is None:
            print('Audio source not defined.')
            return
        
        try:
            file_path = Path(event.path)
            directory = file_path.parent
            file_name = file_path.stem
            file_extension = '.mp3'

            output_path = directory.joinpath(file_name + file_extension)
            source_path = Path(self.application.get_audio_source())
            copyfile(source_path, output_path)

        except Exception as error:
            print_exc()
            self.application.show_danger_banner(str(error))

        else:
            self.application.show_success_banner('File successfully saved.')


class CustomAppBar(ft.AppBar):
    def __init__(self) -> None:
        super().__init__()
        self.title = ft.Text()
        self.title.value = 'Google Text-to-Speech'
        self.title.theme_style = ft.TextThemeStyle.TITLE_LARGE

        self.toggle_theme_button = ft.IconButton()
        self.toggle_theme_button.icon = ft.icons.DARK_MODE
        self.actions.append(self.toggle_theme_button)

        self.leading = ft.Icon()
        self.leading.name = ft.icons.KEYBOARD


class Application:
    def __init__(self, page: ft.Page) -> None:
        # page.
        self.page = page
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.window_width = self.page.window_height = 500
        self.page.title = 'gtts-gui'
        
        # appbar.
        self.appbar = CustomAppBar()
        self.page.appbar = self.appbar

        # controllers.
        self.file_picker = ft.FilePicker()

        self.lang_dropdown = ft.Dropdown()
        self.lang_dropdown.label = 'Language'
        self.lang_dropdown.expand = True

        self.domain_dropdown = ft.Dropdown()
        self.domain_dropdown.label = 'Top-Level Domain'
        self.domain_dropdown.expand = True

        self.input_field = ft.TextField()
        self.input_field.label = 'Input'
        self.input_field.multiline = True
        self.input_field.expand = True

        self.progress_ring = ft.ProgressRing()
        self.progress_ring.value = None
        self.progress_ring.visible = False

        self.start_tts_button = ft.FloatingActionButton()
        self.start_tts_button.icon = ft.icons.START
        self.start_tts_button.text = 'Start Speech Generation'

        self.play_button = ft.ElevatedButton()
        self.play_button.icon = ft.icons.PLAYLIST_PLAY
        self.play_button.text = 'Play'
        self.play_button.expand = True

        self.pause_button = ft.ElevatedButton()
        self.pause_button.icon = ft.icons.STOP
        self.pause_button.text = 'Pause'
        self.pause_button.expand = True

        self.save_button = ft.ElevatedButton()
        self.save_button.icon = ft.icons.DOWNLOAD
        self.save_button.text = 'Save'
        self.save_button.expand = True

        self.audio_controllers = ft.Row()
        self.audio_controllers.controls.append(self.play_button)
        self.audio_controllers.controls.append(self.pause_button)
        self.audio_controllers.controls.append(self.save_button)
        self.audio_controllers.alignment = ft.MainAxisAlignment.CENTER

        self.audio = ft.Audio()
        self.audio.volume = 1
        self.audio.autoplay = True

        content = ft.Column()
        content.scroll = ft.ScrollMode.AUTO
        content.controls.append(ft.Row([self.lang_dropdown, self.domain_dropdown]))
        content.controls.append(ft.Row([self.input_field]))
        content.controls.append(ft.Row([self.progress_ring, self.start_tts_button], alignment=ft.MainAxisAlignment.CENTER))
        content.controls.append(self.audio_controllers)

        container = ft.Container(content)
        container.border = ft.border.all(5, ft.colors.TRANSPARENT)
        container.width = 600
        container.expand = True

        self.page.controls.append(container)
        self.page.controls.append(self.file_picker)
        self.page.update()

        # initial state.
        self.hide_audio_controllers()
        self.active_dark_mode()

        # debug
        # self.show_success_banner('success')

    def active_dark_mode(self) -> None:
        self.page.theme_mode = ft.ThemeMode.DARK
        self.appbar.toggle_theme_button.icon = ft.icons.LIGHT_MODE
        self.page.update()

    def active_light_mode(self) -> None:
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.appbar.toggle_theme_button.icon = ft.icons.DARK_MODE
        self.page.update()

    def toggle_theme_mode(self) -> None:
        match(self.page.theme_mode):
            case ft.ThemeMode.DARK:
                self.active_light_mode()
            case ft.ThemeMode.LIGHT:
                self.active_dark_mode()

    def open_save_file(
        self, 
        file_type: Optional[str] = None, 
        allowed_extensions: Optional[List[str]] = None,
        on_result: Optional[Callable] = None
    )  -> None:
        self.file_picker.on_result = on_result
        self.file_picker.save_file(file_type=file_type, allowed_extensions=allowed_extensions)

    def start_progress_ring(self) -> None:
        self.progress_ring.visible = True
        self.progress_ring.value = None
        self.page.update()

    def stop_progress_ring(self) -> None:
        self.progress_ring.visible = False
        self.progress_ring.value = 0.0
        self.page.update()

    def play_audio(self) -> None:
        print('audio source: {}'.format(self.audio.src))
        if self.audio.src is not None:
            self.audio.play()

    def pause_audio(self) -> None:
        print('audio source: {}'.format(self.audio.src))
        if self.audio.src is not None:
            self.audio.pause()

    def hide_audio_controllers(self) -> None:
        self.audio_controllers.visible = False
        self.page.update()

    def show_audio_controllers(self) -> None:
        self.audio_controllers.visible = True
        self.page.update()

    def show_input_error_text(self, message: str) -> None:
        self.input_field.error_text = message
        self.page.update()

    def show_success_banner(self, message: str) -> None:
        text = ft.Text()
        text.value = message
        text.text_align = ft.TextAlign.LEFT
        text.theme_style = ft.TextThemeStyle.LABEL_LARGE
        text.color = ft.colors.WHITE
        text.selectable = True
        text.expand = True

        icon = ft.Icon()
        icon.name = ft.icons.CHECK
        icon.size = 33
        icon.color = ft.colors.WHITE

        close_button = ft.TextButton()
        close_button.text = 'Close'
        close_button.icon = ft.icons.CLOSE
        close_button.on_click = lambda _event: self.page.close_banner()

        content = ft.Row()
        content.controls.append(icon)
        content.controls.append(text)

        banner = ft.Banner()
        banner.bgcolor = ft.colors.GREEN_500
        banner.actions.append(close_button)
        banner.content = content
        self.page.show_banner(banner)

    def show_danger_banner(self, message: str) -> None:
        text = ft.Text()
        text.value = message
        text.theme_style = ft.TextThemeStyle.LABEL_LARGE
        text.text_align = ft.TextAlign.LEFT
        text.color = ft.colors.WHITE
        text.selectable = True
        text.expand = True

        icon = ft.Icon()
        icon.name = ft.icons.WARNING
        icon.size = 33
        icon.color = ft.colors.WHITE

        close_button = ft.TextButton()
        close_button.text = 'Close'
        close_button.icon = ft.icons.CLOSE
        close_button.on_click = lambda _event: self.page.close_banner()

        content = ft.Row()
        content.controls.append(icon)
        content.controls.append(text)

        banner = ft.Banner()
        banner.bgcolor = ft.colors.RED
        banner.actions.append(close_button)
        banner.content = content
        self.page.show_banner(banner)

    def close_banner(self) -> None:
        self.page.close_banner()

    def clear_input_error_text(self) -> None:
        self.input_field.error_text = ''
        self.page.update()

    def focus_input_field(self) -> None:
        self.input_field.focus()

    def get_input(self) -> str:
        return self.input_field.value

    def get_lang(self) -> Optional[str]:
        return self.lang_dropdown.value

    def get_domain(self) -> Optional[str]:
        return self.domain_dropdown.value

    def get_audio_source(self) -> Optional[str]:
        return self.audio.src
    
    def set_lang(self, lang: str) -> None:
        self.lang_dropdown.value = lang
        self.page.update()

    def set_domain(self, domain: str) -> None:
        self.domain_dropdown.value = domain
        self.page.update()
    
    def set_lang_options(self, options: List[str]) -> None:
        self.lang_dropdown.options.clear()
        for option in options:
            self.lang_dropdown.options.append(ft.dropdown.Option(option))
        self.page.update()

    def set_domain_options(self, options: List[str]) -> None:
        self.domain_dropdown.options.clear()
        for option in options:
            self.domain_dropdown.options.append(ft.dropdown.Option(option))
        self.page.update()
    
    def set_audio_source(self, source: Path) -> None:
        self.audio.src = source
        self.page.overlay.append(self.audio)
        self.page.update()
        self.audio.play()


def main(page: ft.Page) -> None:
    application = Application(page)
    Constructor(application)


if __name__ == '__main__':
    ft.app(target=main, assets_dir='assets')
