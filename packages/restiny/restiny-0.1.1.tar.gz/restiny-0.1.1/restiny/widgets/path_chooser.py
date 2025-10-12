from pathlib import Path
from typing import Literal

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import Reactive
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Switch

from restiny.utils import filter_paths
from restiny.widgets import CustomDirectoryTree


class PathChooserScreen(ModalScreen):
    DEFAULT_CSS = """
    PathChooserScreen {
        align: center middle;
    }

    #modal-content {
        border: heavy black;
        border-title-color: gray;
        background: $surface;
        width: 60%;
        height: 90%;
    }
    """
    BINDINGS = [
        Binding(
            key='escape',
            action='dismiss',
            description='Quit the screen',
            show=False,
        ),
    ]
    show_hidden_files: Reactive[bool] = Reactive(False, init=True)
    show_hidden_dirs: Reactive[bool] = Reactive(False, init=True)

    def compose(self) -> ComposeResult:
        with Vertical(id='modal-content'):
            with Horizontal(id='options', classes='w-auto h-auto mt-1'):
                yield Switch(id='option-show-hidden-files')
                yield Label('Show hidden files', classes='pt-1')

                yield Switch(id='option-show-hidden-dirs')
                yield Label('Show hidden directories', classes='pt-1')

            with Horizontal(classes='h-1fr pt-1 ml-1'):
                yield CustomDirectoryTree(path='/')

            with Horizontal(classes='w-auto h-auto mt-1'):
                yield Input(
                    placeholder='--empty--',
                    disabled=True,
                    type='text',
                    classes='w-1fr',
                )

            with Horizontal(classes='w-auto h-auto mt-1'):
                yield Button(label='Cancel', id='cancel', classes='w-1fr')
                yield Button(label='Confirm', id='choose', classes='w-1fr')

    def on_mount(self) -> None:
        self.modal_content = self.query_one('#modal-content')
        self.switch_show_hidden_files: Switch = self.query_one(
            '#option-show-hidden-files'
        )
        self.switch_show_hidden_dirs: Switch = self.query_one(
            '#option-show-hidden-dirs'
        )
        self.directory_tree = self.query_one(CustomDirectoryTree)
        self.input = self.query_one(Input)
        self.btn_cancel = self.query_one('#cancel')
        self.btn_confirm = self.query_one('#choose')

        self.directory_tree.show_root = False
        self.directory_tree.call_after_refresh(
            callback=lambda: self.directory_tree.expand_by_path(
                target_path=Path.home()
            )
        )

    @on(Switch.Changed, '#option-show-hidden-files')
    def on_toggle_hidden_files(self, message: Switch.Changed) -> None:
        self.show_hidden_files = message.value

    @on(Switch.Changed, '#option-show-hidden-dirs')
    def on_toggle_hidden_directories(self, message: Switch.Changed) -> None:
        self.show_hidden_dirs = message.value

    @on(Button.Pressed, '#cancel')
    def on_cancel(self, message: Button.Pressed) -> None:
        self.dismiss()

    @on(Button.Pressed, '#choose')
    def on_confirm(self, message: Button.Pressed) -> None:
        selected_path = None
        if self.input.value != '':
            selected_path = Path(self.input.value)

        if not self.validate_selected_path(path=selected_path):
            return

        self.dismiss(result=selected_path)

    @on(CustomDirectoryTree.FileSelected)
    @on(CustomDirectoryTree.DirectorySelected)
    def on_path_selected(
        self,
        message: CustomDirectoryTree.FileSelected
        | CustomDirectoryTree.DirectorySelected,
    ) -> None:
        self.input.value = str(message.path)
        self.input.tooltip = str(message.path)

    async def watch_show_hidden_files(self, value: bool) -> None:
        if value is True:
            self.directory_tree.filter_paths = lambda paths: filter_paths(
                paths=paths,
                show_hidden_files=True,
                show_hidden_dirs=self.show_hidden_dirs,
            )
        elif value is False:
            self.directory_tree.filter_paths = lambda paths: filter_paths(
                paths=paths,
                show_hidden_files=False,
                show_hidden_dirs=self.show_hidden_dirs,
            )

        await self.directory_tree.reload()

    async def watch_show_hidden_dirs(self, value: bool) -> None:
        if value is True:
            self.directory_tree.filter_paths = lambda paths: filter_paths(
                paths=paths,
                show_hidden_files=self.show_hidden_files,
                show_hidden_dirs=True,
            )
        elif value is False:
            self.directory_tree.filter_paths = lambda paths: filter_paths(
                paths=paths,
                show_hidden_files=self.show_hidden_files,
                show_hidden_dirs=False,
            )

        await self.directory_tree.reload()

    def validate_selected_path(self, path: Path | None) -> bool:
        raise NotImplementedError()


class FileChooserScreen(PathChooserScreen):
    def on_mount(self) -> None:
        super().on_mount()
        self.modal_content.border_title = 'File chooser'

    def validate_selected_path(self, path: Path | None) -> bool:
        if not path or not path.is_file():
            self.app.bell()
            self.notify('Choose a valid file', severity='error')
            return False

        return True


class DirectoryChooserScreen(PathChooserScreen):
    def on_mount(self) -> None:
        super().on_mount()
        self.modal_content.border_title = 'Directory chooser'

    def validate_selected_path(self, path: Path | None) -> bool:
        if not path or not path.is_dir():
            self.app.bell()
            self.notify('Choose a valid directory', severity='error')
            return False

        return True


class PathChooser(Widget):
    DEFAULT_CSS = """
    PathChooser {
        height: auto;
        width: auto;
    }

    Input {
        width: 1fr;
    }

    Button {
        width: auto;
    }
    """

    path: Reactive[Path | None] = Reactive(None, init=True)

    class Changed(Message):
        """
        Sent when the user change the selected path.
        """

        def __init__(self, path: Path | None) -> None:
            super().__init__()
            self.path = path

    @classmethod
    def file(cls, *args, **kwargs) -> 'PathChooser':
        return cls(*args, **kwargs, path_type='file')

    @classmethod
    def directory(cls, *args, **kwargs) -> 'PathChooser':
        return cls(*args, **kwargs, path_type='directory')

    def __init__(
        self, path_type: Literal['file', 'directory'], *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.path_type = path_type

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Input(placeholder='--empty--', disabled=True)
            yield Button(f'  Choose {self.path_type}  ')

    def on_mount(self) -> None:
        self.input = self.query_one(Input)
        self.button = self.query_one(Button)

    @on(Button.Pressed)
    def open_path_chooser(self) -> None:
        def set_path(path: Path | None = None) -> None:
            self.path = path

        if self.path_type == 'file':
            self.app.push_screen(
                screen=FileChooserScreen(),
                callback=set_path,
            )
        elif self.path_type == 'directory':
            self.app.push_screen(
                screen=DirectoryChooserScreen(),
                callback=set_path,
            )

    def watch_path(self, value: Path | None) -> None:
        self.input.value = str(value) if value else ''
        self.input.tooltip = str(value) if value else ''
        self.post_message(message=self.Changed(path=value))
