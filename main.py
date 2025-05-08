from adapters.JsonAdapter import JsonAdapter
from AdaptedSocket import AdaptedSocket
import threading
import time
import os
print (os.getpid())

host = 'localhost'
port = 65432

adapter = JsonAdapter()
listner = AdaptedSocket(host, port, adapter)

def HandleMessage(object:object):
    print(f"Received {type(object)}: {str(object)}")


listner.AttachHandler(HandleMessage)
listener_thread = threading.Thread(target=listner.RunListener, daemon=True)
listener_thread.start()

publisher = AdaptedSocket(host, port, adapter)


publisher.SendMessage({"message":'Hello world'})
time.sleep(2)
publisher.SendMessage(200)
time.sleep(2)
publisher.SendMessage(["one", "two", "three"])
time.sleep(2)
publisher.SendMessage(789.78)
time.sleep(2)

