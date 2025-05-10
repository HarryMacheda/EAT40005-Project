import socket
import json
import time
from datetime import datetime

# Server setup
SERVER_IP = "192.168.0.199"
SERVER_PORT = 50051

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(1)
print(f"Server listening on {SERVER_IP}:{SERVER_PORT}...")

client_socket, client_address = server_socket.accept()
print(f"Connection established with {client_address}")

buffer = ""
log_data = []

try:
    while True:
        data = client_socket.recv(2048)
        if not data:
            continue

        buffer += data.decode("utf-8")

        # Try to parse multiple JSON objects from buffer
        while True:
            try:
                # Attempt to load a full JSON object
                obj, index = json.JSONDecoder().raw_decode(buffer)
                buffer = buffer[index:].lstrip()  # Remove parsed part and strip whitespace

                if obj.get("distance", 0.0) == 0.0 or obj.get("quality", 0) == 0:
                    continue

                # Add timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                obj["timestamp"] = timestamp
                print(f"[{timestamp}] Data logged: {obj}")

                log_data.append(obj)

                with open("lidar_log.json", "w") as f:
                    json.dump(log_data, f, indent=4)

            except json.JSONDecodeError:
                # Wait for more data
                break

except KeyboardInterrupt:
    print("Server interrupted by user.")

client_socket.close()
server_socket.close()
print("Server stopped.")
