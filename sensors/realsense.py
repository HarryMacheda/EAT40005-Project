import pyrealsense2 as rs
import numpy as np

class Realsense():
    def __init__(self):
        print("Camera")

    def GetFramePoints(self):
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        pipeline.start(config)
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()

        pc = rs.pointcloud()
        points = pc.calculate(depth_frame)
        verts = np.asanyarray(points.get_vertices()).view(np.float32).reshape(-1, 3)
        filtered = [ {"x": float(x), "y": float(y), "z": float(z)} for x, y, z in verts if z != 0 ]

        return filtered