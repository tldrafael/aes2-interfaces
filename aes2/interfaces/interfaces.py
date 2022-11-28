from abc import ABC, abstractmethod
import numpy as np
from typing import List, Tuple


Frame = np.ndarray((100, 100, 3), float)
Mask = np.ndarray((100, 100, 1), float)
Polygon = List[Tuple[int, int]]


class Camera:
    @abstractmethod
    def get_frame(self) -> Frame:
        frame = np.zeros_like(Frame)
        return frame


class Segmentor:
    @abstractmethod
    def __call__(self, frame) -> Mask:
        seg_mask = np.zeros_like(Mask)
        return seg_mask


class OccupancyGrid:
    @abstractmethod
    def __call__(self, seg_mask: Mask) -> Frame:
        pass


class PolygonPath:
    @abstractmethod
    def __call__(self, og_frame: Mask) -> Polygon:
        polygon_points = [(0, 0), (1, 2), (2, 3)]
        return polygon_points
