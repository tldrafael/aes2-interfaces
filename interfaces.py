import numpy as np


Frame = np.ndarray((100, 100, 3), float)
Mask = np.ndarray((100, 100, 1), float)
Polygon = list[tuple[int, int]]


class Camera:
    def __init__(self):
        pass

    def get_frame(self) -> Frame:
        frame = np.zeros_like(Frame)
        return frame


class Segmentor:
    def __init__(self):
        pass

    def __call__(self, frame) -> Mask:
        seg_mask = np.zeros_like(Mask)
        return seg_mask


class OccupancyGrid:
    def __init__(self):
        pass

    def __call__(self, seg_mask: Mask) -> Frame:
        og_frame = np.zeros_like(Frame)
        return og_frame


class PolygonPath:
    def __init__(self):
        pass

    def __call__(self, og_frame: Mask) -> Polygon:
        polygon_points = [(0, 0), (1, 2), (2, 3)]
        return polygon_points
