import math
import numpy as np
from allytools.units.length import Length, LengthUnit
from Sensor.pixel import Pixel
from Sensor.bit_depth import BitDepth
from Sensor.sensor_type import SensorFormats, SensorType
class Sensor:
    def __init__(self, horizontal_pixels:int, vertical_pixels:int, pixel:Pixel, bit_depth:BitDepth, sensor_format:SensorFormats, sensor_type:SensorType):
        self.width_pix = horizontal_pixels
        self.height_pix = vertical_pixels
        self.pixel = pixel
        self.bit_depth = bit_depth
        self.sensor_format = sensor_format
        self.sensor_type = sensor_type
        self._calculate_dimensions()

    def _calculate_dimensions(self):
        self.width = self.width_pix * self.pixel.width
        self.height = self.height_pix * self.pixel.height
        self.diagonal = Length(math.sqrt(self.width.value_mm ** 2 + self.height.value_mm ** 2),LengthUnit.MM)

    def quadrant_grid(self, size: int):
        px_mm = self.pixel.length.value_mm
        mid_x_pix = self.width_pix / 2
        mid_y_pix = self.height_pix / 2
        start_x_mm = (mid_x_pix- 0.5) * px_mm
        start_y_mm = (mid_y_pix - 0.5) * px_mm
        end_x_mm = (self.width_pix  - 0.5) * px_mm
        end_y_mm = (self.height_pix - 0.5) * px_mm
        x_centers = np.linspace(start_x_mm, end_x_mm, size)
        y_centers = np.linspace(start_y_mm, end_y_mm, size)
        y_centers = y_centers[::-1]
        x_mm, y_mm = np.meshgrid(x_centers - start_x_mm,y_centers - start_y_mm,indexing="xy")
        grid = np.empty((size, size), dtype=object)
        for iy in range(size):
            for ix in range(size):
                grid[iy, ix] = (float(x_mm[iy, ix]), float(y_mm[iy, ix]))
        return grid
