import os
import socket
import threading


should_exit = False
connected_threads = []
IMAGE_PATH = "static/latest.jpg"


# Function to handle client connections.
# client_socket: The socket object used for communication with the client.
# client_address: The address of the client.
def handle_client(client_socket, client_address):
    global should_exit
    while not should_exit:
        try:
            client_socket.settimeout(1)
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                message = data.decode('utf-8')
                print(f"Received command: {message}")

        except UnicodeDecodeError:
                print(f"Error decoding the received data.")
        except socket.timeout:
            continue
        except socket.error as e:
            print(f"Socket error while communicating with {client_address}: {e}")
            break
        except Exception as e:
            print(f"Error handling the client request: {e}")
            break
    client_socket.close()


def image_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 8001))
        s.listen()
        print(f"🖼️ Bild-Server läuft auf Port 8001")
        while not should_exit:
            conn, addr = s.accept()
            threading.Thread(target=receive_image, args=(conn,), daemon=True).start()


def receive_image(conn):
    try:
        # 4 Bytes = Länge des Bildes
        length_bytes = conn.recv(4)
        if not length_bytes:
            return False
        length = int.from_bytes(length_bytes, byteorder='big')

        # Bilddaten empfangen
        image_data = b''
        while len(image_data) < length:
            packet = conn.recv(length - len(image_data))
            if not packet:
                return False
            image_data += packet

        # Bild speichern
        with open(IMAGE_PATH, 'wb') as f:
            f.write(image_data)
        print(f"📷 Bild gespeichert ({length} Bytes)")
        return True
    except Exception as e:
        print(f"Error receiving image: {e}")
        return False




def send_message(client_socket):
    global should_exit
    while not should_exit:
        try:
            message = input("Enter message to send to client (type 'exit' to quit): ")
            if message.lower() == 'exit':
                should_exit = True
                break
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            break



if __name__ == '__main__':

    # Create a TCP-based socket object.
    # AF_INET indicates the IPv4 address family, and SOCK_STREAM indicates the TCP protocol.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # Bind the socket to all available network interfaces and set the port number to 8000.
    server_address = ('0.0.0.0', 8000)
    server_socket.bind(server_address)

    # Start listening for incoming connections.
    # The maximum number of queued connections is set to 5.
    server_socket.listen(5)
    server_socket.settimeout(1)
    print("Server has started and is listening for connections...")



    while not should_exit:
        try:

            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")
            # Start the thread that receives client messages
            client_thread = (threading.Thread(target=handle_client, args=(client_socket, client_address)))
            client_thread.start()
            connected_threads.append(client_thread)
            # Start the thread that sends messages to the client
            send_thread = (threading.Thread(target=send_message, args=(client_socket,)))
            send_thread.start()
            connected_threads.append(send_thread)

            image_thread = threading.Thread(target=image_server, daemon=True)
            image_thread.start()
            connected_threads.append(image_thread)

        except socket.timeout:
            continue
        except KeyboardInterrupt:
            should_exit = True
            print("shutting down")
        except Exception as e:
            if should_exit:
                print("shutting down caused by client")
                break
            print(f"Error accepting connection: {e}")

    should_exit = True

    server_socket.close()

    for thread in connected_threads:
        thread.join()
    print("Server has stopped.")

