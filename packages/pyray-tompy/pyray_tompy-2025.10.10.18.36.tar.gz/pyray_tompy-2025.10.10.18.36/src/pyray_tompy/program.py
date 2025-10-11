from dataclasses import dataclass
from decimal import Decimal

import pyray as pr

from .camera import CameraConfiguration, Camera
from .cursor import Cursor
from .keyboard import is_left_ctrl_down_and_q_pressed, is_f_pressed, is_left_or_right_alt_down_and_enter_pressed, \
    is_g_pressed, is_backspace_pressed, is_left_ctrl_and_left_shift_down_and_p_pressed, is_h_pressed
from .window import WindowConfiguration, Window


@dataclass
class ProgramConfiguration:
    window_configuration: WindowConfiguration | None
    camera_configuration: CameraConfiguration | None


def new_configuration(configuration: dict) -> ProgramConfiguration:
    window_configuration: WindowConfiguration = WindowConfiguration(**configuration["window"])
    camera_configuration: CameraConfiguration = CameraConfiguration(**configuration["camera"])
    program_configuration: ProgramConfiguration = ProgramConfiguration(**configuration["program"])

    program_configuration.window_configuration = window_configuration
    program_configuration.camera_configuration = camera_configuration

    return program_configuration


class Program:
    _fhd_width = Decimal("1920")
    _fhd_height = Decimal("1080")
    _1k_width = Decimal("1080")
    _1k_height = Decimal("1080")

    def __init__(self, configuration: ProgramConfiguration) -> None:
        self._configuration: ProgramConfiguration = configuration

        self._window: Window = Window(configuration=self._configuration.window_configuration)
        self._camera: Camera = Camera(configuration=self._configuration.camera_configuration)
        self._cursor: Cursor = Cursor()

        self._is_running: bool = True
        self._is_debugging: bool = False

    def run(self) -> None:
        while not pr.window_should_close():
            self.pre_drawing()

            pr.begin_drawing()

            self.drawing_pre_3d()

            pr.begin_mode_3d(self._camera.camera)

            self.drawing_3d()

            pr.end_mode_3d()

            self.drawing_post_3d()

            pr.end_drawing()

            self.post_drawing()

        self.pre_close()

        pr.close_window()

        self.post_close()

    def pre_drawing(self):
        # quit program
        if is_left_ctrl_down_and_q_pressed():
            self._window.close()

        # toggle fullscreen
        if is_f_pressed() or is_left_or_right_alt_down_and_enter_pressed():
            self._window.toggle_fullscreen()

        # set window to windowed FHD landscape; useful for recording software
        if self._is_debugging and is_g_pressed():
            self._window.set_windowed_size(width=self._fhd_width, height=self._fhd_height)

        # set window to windowed 1k*1k landscape; useful for recording software
        if self._is_debugging and is_h_pressed():
            self._window.set_windowed_size(width=self._1k_width, height=self._1k_height)

        # pause program
        if is_backspace_pressed():
            self._is_running = not self._is_running

        # toggle debug
        if is_left_ctrl_and_left_shift_down_and_p_pressed():
            self._is_debugging = not self._is_debugging

        self._camera.update()
        self._cursor.update()

    def drawing_pre_3d(self):
        pr.clear_background(pr.BLUE)

    def drawing_3d(self):
        pass

    def drawing_post_3d(self):
        pass

    def post_drawing(self):
        pass

    def pre_close(self):
        pass

    def post_close(self):
        pass
