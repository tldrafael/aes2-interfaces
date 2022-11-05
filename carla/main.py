import time
import cv2
import carla
import random
import queue
import numpy as np
from .occupancy_grid import OccupancyGrid
import matplotlib.pyplot as plt


def to_bgra_array(image):
    """Convert a CARLA raw image to a BGRA numpy array."""
    array = np.frombuffer(image.raw_data, dtype=np.dtype('uint8'))
    array = np.reshape(array, (image.height, image.width, 4))
    return array


def to_rgb_array(image):
    """Convert a CARLA raw image to a RGB numpy array."""
    array = to_bgra_array(image)
    array = array[:, :, :3]
    array = array[:, :, ::-1]
    return array


def run(add_vehicles=False):
    client = carla.Client('localhost', 2000)
    client.set_timeout(110.0)

    world = client.get_world()
    settings = world.get_settings()
    settings.fixed_delta_seconds = 0.05
    settings.synchronous_mode = True
    world.apply_settings(settings)
    world_map = world.get_map()
    blueprint_library = world.get_blueprint_library()

    ego_bp = random.choice(blueprint_library.filter('vehicle'))
    ego_transform_init = random.choice(world.get_map().get_spawn_points())
    ego_vehicle = world.spawn_actor(ego_bp, ego_transform_init)
    ego_vehicle.set_autopilot(True)
    ego_waypoint = world_map.get_waypoint(ego_transform_init.location)

    if add_vehicles:
        for _ in range(0, 10):
            bp_vehicle = random.choice(blueprint_library.filter('vehicle'))
            random_point = random.choice(world_map.get_spawn_points())
            other_vehicle = world.try_spawn_actor(bp_vehicle, random_point)
            if other_vehicle is not None:
                other_vehicle.set_autopilot(True)

    camera_transform = carla.Transform(carla.Location(x=1.5, z=10), carla.Rotation(pitch=-90))
    camera_bp = blueprint_library.find('sensor.camera.rgb')
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=ego_vehicle)
    image_queue = queue.Queue()
    camera.listen(image_queue.put)

    camera_seg_bp = blueprint_library.find('sensor.camera.semantic_segmentation')
    camera_seg = world.spawn_actor(camera_seg_bp, camera_transform, attach_to=ego_vehicle)
    seg_queue = queue.Queue()
    camera_seg.listen(seg_queue.put)

    cam_height = camera_transform.location.z
    fov = camera_seg_bp.get_attribute('fov').as_float()
    OG = OccupancyGrid(cam_height=cam_height, fov=fov)

    try:
        fig, axs = plt.subplots(1, 3, figsize=(8, 4))
        [a.set_axis_off() for a in axs.ravel()]
        # for i in range(30):
        while True:
            ego_waypoint = random.choice(ego_waypoint.next(1.5))
            ego_vehicle.set_transform(ego_waypoint.transform)
            world.tick(1)

            image = image_queue.get()
            image_seg = seg_queue.get()

            im = to_rgb_array(image)
            im_seg = to_rgb_array(image_seg)[..., 0]
            im_og = OG.get_OG_meters(im_seg)

            # image.save_to_disk('cache/im_%02d.png' % (i))
            # image_seg.save_to_disk('cache/seg_%02d.png' % (i), carla.ColorConverter.CityScapesPalette)
            # cv2.imwrite('cache/og_%02d.png' % (i), im_og * 255)

            for a, arr in zip(axs, [im, im_seg, im_og]):
                a.imshow(arr)
            plt.show(block=False)
            plt.pause(.1)

    except Exception as e:
        print(e)

    for c in (camera, camera_seg):
        c.stop()
        c.destroy()


if __name__ == '__main__':
    run()
