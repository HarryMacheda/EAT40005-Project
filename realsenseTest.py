from adapters.JsonAdapter import JsonAdapter
from AdaptedSocket import AdaptedSocket
from sensors.realsense import Realsense
import threading
import time
import numpy as np
import open3d as o3d


host = 'localhost'
port = 65432

adapter = JsonAdapter()
listner = AdaptedSocket(host, port, adapter)

def HandleMessage(object:object):
    if(type(object) == int):
        return
    points = np.array([[pt["x"], pt["y"], pt["z"]] for pt in object], dtype=np.float64)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    o3d.visualization.draw_geometries([pcd], window_name="Point Cloud Viewer")


listner.AttachHandler(HandleMessage)
listener_thread = threading.Thread(target=listner.RunListener, daemon=True)
listener_thread.start()

publisher = AdaptedSocket(host, port, adapter)
camera = Realsense()
publisher.SendMessage(len(camera.GetFramePoints()))
time.sleep(2)
publisher.SendMessage(camera.GetFramePoints())
time.sleep(2)
publisher.SendMessage(camera.GetFramePoints())
time.sleep(2)
publisher.SendMessage(camera.GetFramePoints())
time.sleep(2)

