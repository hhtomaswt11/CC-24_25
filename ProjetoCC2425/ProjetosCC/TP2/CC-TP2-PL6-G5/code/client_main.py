#from server.NMS_server import NMS_server
from clients.client import Client
import os
import time
import threading
import sys

if __name__ == "__main__":
    # sys.argv[1:] contém os argumentos passados ao script
    if len(sys.argv) < 2:
        print("Necessita de fornecer o client_id e o server_ip!")
        sys.exit(1)

    client_id = sys.argv[1]
    server_ip = sys.argv[2]

    print(f"Client ID: {client_id}")
    print(f"Server IP: {server_ip}")

    #server_ip='10.0.3.2'
    server_port=54321
    
    client1 = Client(server_ip, server_port, client_id)
    client1_thread = threading.Thread(target=client1.listen_for_datagrams)
    client1_thread.daemon = True
    client1_thread.start()

    client1.send_initial_info()

    #time.sleep(150)
    while True:

      option = str(input("\nIntroduza :q para sair "))
      if option == ":q":
         break