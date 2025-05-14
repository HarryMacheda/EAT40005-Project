from adapters.PointStreamAdapter import PointStreamAdapter
from AdaptedSocket import AdaptedSocket
from sensors.realsense import Realsense
import threading
import time
import numpy as np
import open3d as o3d


host = 'localhost'
port = 65432

adapter = PointStreamAdapter()
listner = AdaptedSocket(host, port, adapter)

prevtime = time.time_ns() // 1_000_000
def HandleMessage(object:object):
    global prevtime
    #pcd = o3d.geometry.PointCloud()
    #pcd.points = o3d.utility.Vector3dVector(object)
    #o3d.visualization.draw_geometries([pcd], window_name="Point Cloud Viewer")
    now = time.time_ns() // 1_000_000
    print("Sent " + str(len(object)) + " points in " + str(now - prevtime) + "ms")
    prevtime = time.time_ns() // 1_000_000



listner.AttachHandler(HandleMessage)
listener_thread = threading.Thread(target=listner.RunListener, daemon=True)
listener_thread.start()

publisher = AdaptedSocket(host, port, adapter)
camera = Realsense()

while True:
    publisher.SendMessage(camera.GetFramePoints())



