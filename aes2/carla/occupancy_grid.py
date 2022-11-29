import numpy as np
import cv2
from ..interfaces import OccupancyGrid as InterfaceOccupancyGrid


class OccupancyGrid(InterfaceOccupancyGrid):
    def __init__(self, cam_height=0, fov=90, ix_road=7, ix_marking=6, x_meter_per_pixel=.1, z_meter_per_pixel=.1):
        self.fov = fov
        self.cam_height = cam_height
        fov_rad = fov * np.pi / 180
        self.X_length = np.tan(fov_rad / 2) * cam_height
        self.Z_length = 2 * self.X_length
        self.ix_road = ix_road
        self.ix_marking = ix_marking
        self.x_meter_per_pixel = x_meter_per_pixel
        self.z_meter_per_pixel = z_meter_per_pixel

    def get_left_edge(self, im_seg):
        line_v = np.arange(im_seg.shape[0])
        line_u = (im_seg == self.ix_road).argmax(1)
        return line_u, line_v

    def get_right_edge(self, im_seg):
        line_v = np.arange(im_seg.shape[0])
        line_u = im_seg.shape[1] - (im_seg == self.ix_road)[..., ::-1].argmax(1)
        return line_u, line_v

    def get_lane_mask(self, im_seg):
        left_u, left_v = self.get_left_edge(im_seg)
        right_u, right_v = self.get_right_edge(im_seg)
        im_seg_pos = np.zeros_like(im_seg)
        for v, lu, ru in zip(np.arange(im_seg.shape[0]), left_u, right_u):
            lu_adj = (lu + ru) // 2
            im_seg_pos[v, lu_adj:ru] = 1
        return im_seg_pos

    def get_OG_pixels(self, im_seg):
        lane_mask = self.get_lane_mask(im_seg)
        return lane_mask * (im_seg == self.ix_road)

    def get_OG_meters(self, im_seg):
        im_seg = im_seg[:(im_seg.shape[0] // 2)].copy()
        if not (im_seg == self.ix_marking).any():
            print('Image has no lane markings')
            return np.zeros_like(im_seg)

        im_og = self.get_OG_pixels(im_seg)
        x_pixels_new = int(round(self.X_length / self.x_meter_per_pixel))
        z_pixels_new = int(round(self.Z_length / self.z_meter_per_pixel))
        im_og = cv2.resize(im_og, (z_pixels_new, x_pixels_new), interpolation=cv2.INTER_NEAREST)
        return im_og

    def __call__(self, im_seg):
        return self.get_OG_meters(im_seg)
