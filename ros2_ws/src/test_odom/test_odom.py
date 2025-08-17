import socket
import json
import time
import sys

# Configuration
SERVER_IP = "192.168.68.103"  # Replace with the actual IP address of the Temi robot
SERVER_PORT = 50052        # Matches the SERVER_PORT in the Android code
RECONNECT_DELAY = 5        # Seconds to wait before reconnecting on failure

def connect_to_server():
    """Create and connect a socket to the Temi robot server."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)  # Set timeout for connection
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")
        return client_socket
    except socket.error as e:
        print(f"Connection failed: {e}")
        return None

def receive_data(client_socket):
    """Receive and process data from the server."""
    buffer = ""
    while True:
        try:
            # Receive data in chunks
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                print("Server closed the connection")
                return False

            print(f"Raw data received: {data!r}")  # Log raw data for debugging
            buffer += data

            # Process complete JSON messages (assuming each message ends with \n)
            while '\n' in buffer:
                message, _, buffer = buffer.partition('\n')
                if message.strip():
                    try:
                        # Parse JSON data
                        json_data = json.loads(message)
                        print("Received JSON:", json_data)

                        # Handle different types of messages
                        if json_data.get("type") == "welcome":
                            print(f"Welcome message: {json_data.get('message')}")
                        elif json_data.get("type") == "pong":
                            print(f"Pong received: {json_data.get('timestamp')}")
                        elif json_data.get("timestamp"):
                            # This is a position data message
                            print(f"Position Data - Timestamp: {json_data['timestamp']}, "
                                  f"X: {json_data['x']}, Y: {json_data['y']}, "
                                  f"Yaw: {json_data['yaw']}, Tilt: {json_data['tilt']}, "
                                  f"Status: {json_data['status']}")
                            # Optionally, save to a file or process further
                            save_to_file(json_data)

                    except json.JSONDecodeError as e:
                        print(f"JSON parsing error: {e}, Message: {message!r}")
                        continue  # Skip malformed JSON and continue processing

            # Send a ping to keep the connection alive (optional)
            client_socket.send("ping\n".encode('utf-8'))

        except socket.timeout:
            print("Socket timeout, attempting to reconnect...")
            return False
        except socket.error as e:
            print(f"Socket error: {type(e).__name__}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {e}, Data: {buffer!r}")
            return False

def save_to_file(data):
    """Save received position data to a CSV file."""
    try:
        with open("temi_position_data.csv", "a") as f:
            # Write header if file is empty
            if f.tell() == 0:
                f.write("timestamp,x,y,yaw,tilt,status\n")
            # Write data
            f.write(f"{data['timestamp']},{data['x']},{data['y']},"
                    f"{data['yaw']},{data['tilt']},{data['status'].replace(',', ';')}\n")
    except Exception as e:
        print(f"Error saving to file: {e}")

def main():
    while True:
        client_socket = connect_to_server()
        if client_socket:
            try:
                # Main loop to receive data
                if not receive_data(client_socket):
                    client_socket.close()
            except KeyboardInterrupt:
                print("Closing connection...")
                client_socket.close()
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                client_socket.close()
        print(f"Reconnecting in {RECONNECT_DELAY} seconds...")
        time.sleep(RECONNECT_DELAY)

if __name__ == "__main__":
    main()
