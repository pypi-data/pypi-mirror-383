from dataclasses import dataclass
from decimal import Decimal

import pyray as pr

from .window import get_window_aspect_ratio


class FOVY:
    def __init__(self, minimum_vertical_units: float, minimum_horizontal_units: float) -> None:
        self._minimum_vertical_units: float = minimum_vertical_units
        self._minimum_horizontal_units: float = minimum_horizontal_units

    def calculate(self) -> float:
        # Correct fovy for window aspect ratio
        window_aspect_ratio: Decimal = get_window_aspect_ratio()
        vertical_fovy: float = self._minimum_vertical_units
        horizontal_fovy: float = self._minimum_horizontal_units / float(window_aspect_ratio)
        greatest_fovy: float = max(vertical_fovy, horizontal_fovy)
        return greatest_fovy


@dataclass
class CameraConfiguration:
    position: pr.Vector3
    target: pr.Vector3
    up: pr.Vector3
    projection: pr.CameraProjection
    fovx_minimum_horizontal_units: float
    fovy_minimum_vertical_units: float


class Camera:
    def __init__(self, configuration: CameraConfiguration) -> None:
        self._configuration: CameraConfiguration = configuration

        self._fovy: FOVY = FOVY(minimum_vertical_units=self._configuration.fovy_minimum_vertical_units,
                                minimum_horizontal_units=self._configuration.fovx_minimum_horizontal_units)

        self._camera = pr.Camera3D(self._configuration.position,
                                   self._configuration.target,
                                   self._configuration.up,
                                   self._fovy.calculate(),
                                   self._configuration.projection)

    @property
    def camera(self) -> pr.Camera3D:
        return self._camera

    def update(self) -> None:
        self.camera.fovy = self._fovy.calculate()
