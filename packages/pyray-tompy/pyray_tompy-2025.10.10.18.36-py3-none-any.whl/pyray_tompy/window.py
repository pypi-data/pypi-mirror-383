from dataclasses import dataclass, field
from decimal import Decimal

import pyray as pr

from vector_tompy.area2 import Area2
from vector_tompy.vector2 import Vector2


class MonitorSize(Area2):
    pass


class WindowSize(Area2):
    pass


class WindowPosition(Vector2):
    pass


@dataclass
class WindowRectangle:
    position: WindowPosition
    size: WindowSize


@dataclass
class MonitorMode:
    number: int
    size: MonitorSize
    refresh_rate: int


@dataclass
class FullscreenMode:
    monitor: int
    size: MonitorSize
    refresh_rate: int


@dataclass
class WindowedMode:
    rectangle: WindowRectangle
    refresh_rate: int


def get_current_window_monitor() -> int:
    """Pyray check for which system monitor the pyray window is located on."""
    monitor_number: int = 0  # Default monitor number

    window_pos: pr.Vector2 = pr.get_window_position()
    monitor_count: int = pr.get_monitor_count()

    for monitor in range(monitor_count):
        monitor_pos: pr.Vector2 = pr.get_monitor_position(monitor)
        monitor_width: int = pr.get_monitor_width(monitor)
        monitor_height: int = pr.get_monitor_height(monitor)

        is_window_inside_monitor_x_axis: bool = monitor_pos.x <= window_pos.x < monitor_pos.x + monitor_width
        is_window_inside_monitor_y_axis: bool = monitor_pos.y <= window_pos.y < monitor_pos.y + monitor_height
        is_window_inside_monitor_area: bool = is_window_inside_monitor_x_axis and is_window_inside_monitor_y_axis

        if is_window_inside_monitor_area:
            monitor_number = monitor

    return monitor_number


def get_monitor_size(monitor: int) -> MonitorSize:
    width: int = pr.get_monitor_width(monitor)
    height: int = pr.get_monitor_height(monitor)
    size: MonitorSize = MonitorSize(width=Decimal(width), height=Decimal(height))
    return size


def get_centered_window_position(monitor_size: MonitorSize, window_size: WindowSize) -> WindowPosition:
    centered_window_position: WindowPosition = WindowPosition(
        x=((monitor_size.width - window_size.width) // Decimal(2)).to_integral(),
        y=((monitor_size.height - window_size.height) // Decimal(2)).to_integral())
    return centered_window_position


def set_window_from_monitor(fraction: Decimal) -> None:
    monitor: int = get_current_window_monitor()
    monitor_size: MonitorSize = get_monitor_size(monitor=monitor)

    window_size: WindowSize = WindowSize(width=(monitor_size.width * fraction).to_integral(),
                                         height=(monitor_size.height * fraction).to_integral())
    pr.set_window_size(int(window_size.width), int(window_size.height))


def set_and_center_window_from_monitor(fraction: Decimal) -> None:
    monitor: int = get_current_window_monitor()
    monitor_size: MonitorSize = get_monitor_size(monitor=monitor)

    window_size: WindowSize = WindowSize(width=(monitor_size.width * fraction).to_integral(),
                                         height=(monitor_size.height * fraction).to_integral())
    pr.set_window_size(int(window_size.width), int(window_size.height))

    centered_window_position: WindowPosition = get_centered_window_position(monitor_size=monitor_size,
                                                                            window_size=window_size)
    pr.set_window_position(int(centered_window_position.x), int(centered_window_position.y))


def set_and_center_window(window_size: WindowSize) -> None:
    monitor: int = get_current_window_monitor()
    monitor_size: MonitorSize = get_monitor_size(monitor=monitor)

    pr.set_window_size(int(window_size.width), int(window_size.height))

    centered_window_position: WindowPosition = get_centered_window_position(monitor_size=monitor_size,
                                                                            window_size=window_size)
    pr.set_window_position(int(centered_window_position.x), int(centered_window_position.y))


def get_fullscreen_mode() -> FullscreenMode:
    monitor: int = get_current_window_monitor()
    size: MonitorSize = get_monitor_size(monitor=monitor)
    refresh_rate: int = pr.get_monitor_refresh_rate(monitor)
    fullscreen_mode: FullscreenMode = FullscreenMode(monitor=monitor, size=size, refresh_rate=refresh_rate)
    return fullscreen_mode


def set_and_position_window(window_rectangle: WindowRectangle) -> None:
    pr.set_window_size(int(window_rectangle.size.width), int(window_rectangle.size.height))
    pr.set_window_position(int(window_rectangle.position.x), int(window_rectangle.position.y))


def get_monitor_pointer(monitor_number: int):
    monitor_count_c_int = pr.ffi.new("int *")
    monitor_list = pr.glfw_get_monitors(monitor_count_c_int)
    monitor_pointer = monitor_list[monitor_number]
    return monitor_pointer


def set_window_monitor_glfw(monitor_number: int | None,
                            position_x: int,
                            position_y: int,
                            width: int,
                            height: int,
                            refresh_rate: int) -> None:
    window_pointer = pr.get_window_handle()

    if monitor_number is not None:
        monitor_pointer = get_monitor_pointer(monitor_number=monitor_number)
    else:
        monitor_pointer = None

    pr.glfw_set_window_monitor(window_pointer,
                               monitor_pointer,
                               position_x,
                               position_y,
                               width,
                               height,
                               refresh_rate)


def set_fullscreen_glfw(mode: FullscreenMode) -> None:
    set_window_monitor_glfw(monitor_number=mode.monitor,
                            position_x=0,
                            position_y=0,
                            width=int(mode.size.width),
                            height=int(mode.size.height),
                            refresh_rate=mode.refresh_rate)


def set_windowed_glfw(mode: WindowedMode) -> None:
    set_window_monitor_glfw(monitor_number=None,
                            position_x=int(mode.rectangle.position.x),
                            position_y=int(mode.rectangle.position.y),
                            width=int(mode.rectangle.size.width),
                            height=int(mode.rectangle.size.height),
                            refresh_rate=mode.refresh_rate)


def get_window_position() -> WindowPosition:
    position: pr.Vector2 = pr.get_window_position()
    window_position: WindowPosition = WindowPosition(x=Decimal(position.x).to_integral(),
                                                     y=Decimal(position.y).to_integral())
    return window_position


def get_window_size() -> WindowSize:
    width: int = pr.get_screen_width()
    height: int = pr.get_screen_height()
    window_size: WindowSize = WindowSize(width=Decimal(width), height=Decimal(height))
    return window_size


def get_window_position_and_size() -> WindowRectangle:
    position: WindowPosition = get_window_position()
    size: WindowSize = get_window_size()
    rectangle: WindowRectangle = WindowRectangle(position=position, size=size)
    return rectangle


def get_window_aspect_ratio() -> Decimal:
    size: WindowSize = get_window_size()
    window_aspect_ratio: Decimal = size.width / size.height
    return window_aspect_ratio


def update_restore_position_values(restore_values: WindowRectangle) -> WindowRectangle:
    fullscreen_mode: FullscreenMode = get_fullscreen_mode()
    position: WindowPosition = get_centered_window_position(monitor_size=fullscreen_mode.size,
                                                            window_size=restore_values.size)
    updated_values: WindowRectangle = WindowRectangle(position=position, size=restore_values.size)
    return updated_values


@dataclass
class WindowConfiguration:
    is_resizable_window: bool
    is_rendering_antialiased: bool
    target_frames_per_second: int
    window_title: str
    start_window_size_width: int
    start_window_size_height: int
    is_start_window_size_fraction_of_screen: bool
    start_window_size_fraction_of_screen: Decimal
    is_start_window_fullscreen: bool
    is_first_fullscreen_to_windowed: bool = True
    is_fullscreen: bool = False
    restore_position_and_size: WindowRectangle = field(default_factory=get_window_position_and_size)


# TODO: separate handling/storage of config and state
class Window:
    def __init__(self, configuration: WindowConfiguration) -> None:
        self._configuration = configuration

        if self._configuration.is_resizable_window: pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        if self._configuration.is_rendering_antialiased: pr.set_config_flags(pr.ConfigFlags.FLAG_MSAA_4X_HINT)

        self._initiate()

    def _initiate(self) -> None:
        pr.set_target_fps(self._configuration.target_frames_per_second)

        # Placeholder window size before resizing
        pr.init_window(self._configuration.start_window_size_width,
                       self._configuration.start_window_size_height,
                       self._configuration.window_title)

        if self._configuration.is_start_window_size_fraction_of_screen:
            set_and_center_window_from_monitor(fraction=self._configuration.start_window_size_fraction_of_screen)

        if self._configuration.is_start_window_fullscreen:
            self.toggle_fullscreen()

    def toggle_fullscreen(self) -> None:
        fullscreen_mode: FullscreenMode = get_fullscreen_mode()

        if self._configuration.is_fullscreen:
            # Sometimes pr.get_window_position() has wrong output when program starts in fullscreen, so we help it out
            if self._configuration.is_start_window_fullscreen and self._configuration.is_first_fullscreen_to_windowed:
                self._configuration.is_first_fullscreen_to_windowed = False
                self._configuration.restore_position_and_size = update_restore_position_values(
                    restore_values=self._configuration.restore_position_and_size)

            windowed_mode: WindowedMode = WindowedMode(rectangle=self._configuration.restore_position_and_size,
                                                       refresh_rate=fullscreen_mode.refresh_rate)
            set_windowed_glfw(mode=windowed_mode)
        else:
            self._configuration.restore_position_and_size = get_window_position_and_size()
            set_fullscreen_glfw(mode=fullscreen_mode)

        self._configuration.is_fullscreen = not self._configuration.is_fullscreen

    def set_windowed_size(self, width: Decimal, height: Decimal):
        # TODO: figure out if it is possible to set a window size that stretches outside of the monitor size
        #       currently either raylib or gnome is restricting window size to be inside screen upon resizing
        if self._configuration.is_fullscreen:
            self.toggle_fullscreen()
        window_size: WindowSize = WindowSize(width=width, height=height)
        set_and_center_window(window_size=window_size)

    @staticmethod
    def close() -> None:
        pr.glfw_set_window_should_close(pr.get_window_handle(), True)
