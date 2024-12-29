import shutil
from server.NMS_server import NMS_server
from clients.client import Client
import os
import time
import threading

if __name__ == "__main__":
    # Initialize the NMS server
    nms_server = NMS_server()

    # Load tasks from JSON
    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(current_dir, "tasks.json")
    nms_server.parse_json(json_path)

    server_ip='127.0.0.1'
    server_port=54321


    # Start the server in a separate thread
    server_thread = threading.Thread(target=nms_server.listen_for_datagrams, args=(nms_server.UDP_socket,))
    server_thread.daemon = True
    server_thread.start()

    # Give the server a moment to start up
    time.sleep(1)

    # Create a UDP client instance
    client1 = Client(server_ip, server_port, 'n1')

    client1_thread = threading.Thread(target=client1.listen_for_datagrams)
    client1_thread.daemon = True
    client1_thread.start()

    client1.send_initial_info()

    client2 = Client(server_ip, server_port, 'n2')

    client2_thread = threading.Thread(target=client2.listen_for_datagrams)
    client2_thread.daemon = True
    client2_thread.start()

    client2.send_initial_info()

    client3 = Client(server_ip, server_port, 'n3')

    client3_thread = threading.Thread(target=client3.listen_for_datagrams)
    client3_thread.daemon = True
    client3_thread.start()

    client3.send_initial_info()
    """
    # Example of sending a datagram
    sequence_number = 1
    message_type = 1  # Example message type
    data = b'Hello, this is a test message.'  # Data to be sent

    client.send_UDP_datagram(sequence_number, message_type, data)

    # Close the client socket
    """
    time.sleep(20)

    client1.close()
    client2.close()
    client3.close()

    client1_thread.join()
    client2_thread.join()
    client3_thread.join()


    # Optionally, you can join the server thread if needed
    nms_server.close()

    server_thread.join()