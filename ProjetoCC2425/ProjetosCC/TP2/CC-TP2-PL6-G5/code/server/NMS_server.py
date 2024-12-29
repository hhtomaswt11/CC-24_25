import json
import socket
import struct
import threading
from tasks.parser import parseTasks
from tasks.config import Config, Device_metrics, AlertflowConditions, LatencyConfig, Link_metrics
from tasks.task import Task
from tasks.tasks import Tasks
from clients.clients import Clients
from clients.client_server import ClientServer
from server.NMS_server_UDP import NMS_server_UDP
from misc.sendMessage import sendMessage
from misc.openFile import openFile

import random
import time

class NMS_server:

    def __init__(self, storage_path):
        self.lastTask = 1
        self.tasks = Tasks()
        self.waitingTasks = {}
        self.currentTask = 1
        self.clients = Clients()
        self.UDP_socket = self.setup_UDP_socket(('', 54321))  # Initialize the UDP socket
        self.TCP_socket = self.setup_TCP_socket(('', 54322))  # Initialize the TCP socket
        self.threads = []
        self.cond = threading.Condition()
        self.lock = threading.Lock()
        self._stop_event = threading.Event()
        self.storage_path = storage_path

        # Inicia uma thread para escutar clientes UDP
        #udp_thread = threading.Thread(target=self.listen_for_datagrams, args=(self.UDP_socket,))
        #udp_thread.start()
        #self.threads.append(udp_thread)

    def setup_UDP_socket(self, addr):
        """
        Creates and sets up a UDP socket.

        This function creates a UDP socket, binds it to a given address, and 
        returns the configured socket object. The address must specify the host 
        and port to which the socket will be bound.

        Parameters:
            addr (tuple): A tuple containing the host (as a string) and port 
                        (as an integer) to bind the socket to. 
                        Example: ('10.0.0.4', 8080).

        Returns:
            socket.socket: The configured UDP socket object.

        Example:
            >>> my_udp_socket = setup_UDP_socket(('10.0.0.2', 8080))
        """

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(addr)
        return udp_socket
    
    def setup_TCP_socket(self, addr):
        """
        Creates and sets up a TCP socket.

        This function creates a TCP socket, binds it to a given address, and 
        returns the configured socket object. The address must specify the host 
        and port to which the socket will be bound.

        Parameters:
            addr (tuple): A tuple containing the host (as a string) and port 
                        (as an integer) to bind the socket to. 
                        Example: ('10.0.0.4', 8080).

        Returns:
            socket.socket: The configured TCP socket object.

        Example:
            >>> my_tcp_socket = setup_TCP_socket(('10.0.0.4', 8080))
        """

        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        TCP_socket.bind(addr)
        return TCP_socket


    def parse_json(self, path: str):
        """
        Parses a JSON file containing tasks and updates the task manager.

        This function reads a JSON file from the specified path, processes each task 
        in the file, and adds it to the task manager. It assigns a unique ID to each 
        task and ensures the tasks are iteratively accessible.

        Parameters:
            path (str): The file path to the JSON file containing the tasks.

        Behavior:
            - If the JSON file is empty, no tasks are added, and the function exits.
            - Iterates through tasks in the JSON and processes them using the 
            `parseTasks` function.
            - Increments a `lastTask` counter for each task added.
            - After processing, iterates through tasks by ID to ensure all tasks 
            are successfully added.

        Example:
            >>> obj.parse_json("tasks.json")

        Notes:
            - The structure of the JSON file and the `parseTasks` function are 
            assumed to follow a specific contract.
            - The function prints a blank line when the JSON file is empty or non-empty,
            but the specific behavior can be further refined.

        Returns:
            None
        """
        # Existing code for parsing JSON remains unchanged
        with open(path, "r") as file:
            tasks_json = json.load(file)

        if not tasks_json:
            print(" ")  # Placeholder for handling empty JSON
        else:
            print(" ")  # Placeholder for handling non-empty JSON

        for task in tasks_json:
            task_obj = parseTasks(self.lastTask, task)
            self.lastTask += 1
            self.tasks.add_task(task_obj)

        id = 1
        while True:
            t = self.tasks.get_task(str(id))
            if not t:
                break  # Exit loop if task is not found
            # Uncomment for debugging:
            # print(f"{t.task_id}  {t.type} {t.devices}")
            id += 1





    def processTask(self):

        while not self._stop_event.is_set() and self.currentTask <= len(self.tasks):
         
            task = self.tasks.get_task(self.currentTask)
            devices = task.getDevices()
            maxT = 3
            task_Threads = []
            nms_udp = NMS_server_UDP(self.storage_path)

            if task.config.link_metrics.use_iperf == True and self.clients.at_least_one(devices):
                server = self.clients.get_client(task.config.link_metrics.server)
                if not server:
                   time.sleep(5)
                   server = self.clients.get_client(task.config.link_metrics.server)
                if server:
                    task.config.link_metrics.server_address = server.address[0]
                    sendMessage(self.UDP_socket, server.address, str(task.config.link_metrics.duration), 4)
                else:
                    for d in devices:
                        #self.waitingTasks[d] = task
                      if d not in self.waitingTasks:
                      # Initialize a new list if the key doesn't exist
                        self.waitingTasks[d] = []
                        # Append the new task to the list of tasks for the key
                        #else:
                      self.waitingTasks[d].append(task)
                    break

            for d in devices:
                client = self.clients.get_client(d)
                if not client:
                    time.sleep(1)
                    client = self.clients.get_client(d)

                if client:    
                    
                    with self.cond:
                        thread = threading.Thread(target=nms_udp.listen_for_datagrams, name =f"Thread-{d}", args=(self.cond,d, client.socket, client.address, task,))
                        nms_udp.threads[d] = thread
                        thread.daemon = True
                        thread.start()
                    #self.sendMessage(self.UDP_socket, client.address, task.to_bytes())    

                else:
                    if d not in self.waitingTasks:
                      # Initialize a new list if the key doesn't exist
                      self.waitingTasks[d] = []
                    # Append the new task to the list of tasks for the key
                    #else:
                    self.waitingTasks[d].append(task)

            while nms_udp.threads:
                time.sleep(0.1)

            self.currentTask+=1
        self.processWaitingTask()

    def processWaitingTask(self):
        while not self._stop_event.is_set() and len(self.waitingTasks) != 0:
            devices = self.clients.get_client_ids()
            nms_udp = NMS_server_UDP(self.storage_path)


            for d in devices:
                task = None
                client = self.clients.get_client(d)
                if d in self.waitingTasks:
                    if len(self.waitingTasks[d]) != 0:
                        task = self.waitingTasks[d].pop()
                if task:
                    if task.config.link_metrics.use_iperf == True: 
                        server = self.clients.get_client(task.config.link_metrics.server)
                        if server:
                            task.config.link_metrics.server_address = server.address[0]
                            sendMessage(self.UDP_socket, server.address, str(task.config.link_metrics.duration), 4)
                    with self.cond:
                        self.waitingTasks
                        thread = threading.Thread(target=nms_udp.listen_for_datagrams, name =f"Thread-{d}", args=(self.cond,d, client.socket, client.address, task,))
                        nms_udp.threads[d] = thread
                        thread.daemon = True
                        thread.start()

            while nms_udp.threads:
                time.sleep(0.1)




    def createPort(self):
        """
        Generates a random and unique port number for communication.

        This function creates a random port number within the valid range (1–65535) 
        and ensures that it does not conflict with the ports already in use by existing clients.

        Behavior:
            - Generates a random port using `random.randint`.
            - Checks the list of connected clients to ensure the generated port is not already in use.
            - Regenerates the port if a conflict is detected, ensuring uniqueness.

        Returns:
            int: A valid and unique port number for communication.

        Notes:
            - The function uses the `getsockname` method of the client sockets to retrieve the currently used port.
            - Assumes that `self.clients.to_dict()` provides a dictionary of client objects, where each client has a valid `socket` attribute.

        Example:
            >>> storage_path = "/storage"
            >>> server = NMS_server(storage_path)
            >>> port = server.createPort()
            >>> print(f"Generated port: {port}")
        """

        port = random.randint(1, 65535)
        clients = self.clients.to_dict()  # Corrected to call to_dict()

        # Iterate over client objects
        for id, client in clients.items():  # `client` should be a `ClientServer` instance
            # Ensure `client` has a valid socket and that it’s a socket object
            if hasattr(client, 'socket') and hasattr(client.socket, 'getsockname'):
                if client.socket.getsockname()[1] == port:
                    port = random.randint(1, 65535)

        return port



    def listen_for_datagrams(self, socket):
        """
        Listens for incoming datagrams and processes them.

        This function continuously listens for incoming datagrams on the provided 
        socket until the stop event is triggered. When a datagram is received, 
        it is passed to the `handle_datagram` method for processing. The function 
        handles exceptions related to socket communication and stops listening 
        on errors.

        Behavior:
            - Listens for incoming datagrams using the provided socket.
            - When a datagram is received, the data and sender's address are passed to `handle_datagram`.
            - Stops listening and exits on specific socket errors (`ConnectionResetError`, `OSError`).

        Args:
            socket (socket.socket): The socket used to receive the datagrams.

        Example:
            >>> NMS_server(storage_path).listen_for_datagrams(socket)
        """

        buffer_size = 1024
        while not self._stop_event.is_set():
            try:
                #print(f"Server listening:\n")
                data, addr = socket.recvfrom(buffer_size)
                #print(f'Data received')
                if data:
                    self.handle_datagram(data, addr)
            except ConnectionResetError as e:
                #print(f"Connection reset error: {e}")
                break
            except OSError as e:
                #print(f"OS error (likely socket issue): {e}")
                break

    def handle_datagram(self, data, addr):
        """
        Processes incoming datagrams, extracts relevant data, and manages client registration.

        This function decodes the received datagram, extracts important fields such as headers and payload, 
        and performs actions based on the message type. It handles client registration, port creation, 
        and socket setup for further communication. If it's the first client, it initiates the task processing.

        Behavior:
            - Decodes the incoming datagram into payload and header data.
            - Checks the `messageType` field to determine the type of message (e.g., client registration).
            - If the message type is `0` (client registration), it extracts client details and registers the client.
            - Creates a unique port for the client and sets up a UDP socket for communication.
            - If it's the first registered client, it starts the task processing in a separate thread.
            - Handles other message types as required.

        Args:
            data (bytes): The raw datagram data received, including headers and payload.
            addr (tuple): The address (IP and port) of the sender.

        Example:
            >>> NMS_server(storage_path).handle_datagram(data, addr)
        """

        # Decodifique os dados recebidos de bytes para string
        #print(f"Received raw data: {data}")
        payload = data[14:]
        payload = payload.decode('utf-8')  # 'ignore' skips invalid bytes
        headers = data[:10]
        sequence = data[10:14]
        source_port, dest_port, length, checksum, messageType = struct.unpack('!HHHHH', headers)
        sequence_number, sequence_length = struct.unpack('!HH', sequence)
        #print(f"Received data: {payload}\n")
        #print(f"Adrr: {addr}\n")

        
        # Verifique se a mensagem contém um ID para processar os dados do cliente
        if messageType == 0:

            # Obtenha os dados do cliente e valide se todos os campos estão presentes
            client_id = payload
            client_addr = addr

            port = self.createPort()

            socket = self.setup_UDP_socket(('0.0.0.0', port))

            sendMessage(socket, client_addr, str(port), 0)



            if client_id and client_addr:
                with self.lock:
                    # Converta a porta para inteiro e adicione o cliente
                    #client = Client(client_id, server_ip, int(server_port))
                
                    client = ClientServer(addr, socket)
                    self.clients.add_client(client_id, client)
                    #print(f"Client {client_id} added with Address {client_addr}")
                    #print(f"{str(self.clients.to_dict())}\n")

                    if len(self.clients) == 1:
                        task_thread = threading.Thread(target=self.processTask)
                        task_thread.daemon = True
                        task_thread.start()
                        self.threads.append(task_thread)
                    #else: 
                        #print("Erro. Length not valid")
                
            #else:
                #print("Erro: Dados do cliente ausentes ou incompletos na mensagem de registro.")
        #else:
            # Processa outras mensagens
            #print(f"Received non-registration data: {payload}")

    def close(self):
        """
        Stops ongoing processes and closes network sockets.

        This function sets the stop event to terminate ongoing operations, 
        waits for the first thread in the `threads` list to complete, and then 
        closes both the UDP and TCP sockets. It ensures that all resources are 
        properly released before shutting down.

        Behavior:
            - Sets the `_stop_event` to signal the termination of ongoing operations.
            - Waits for the first thread in the `threads` list to finish using `join()`.
            - Closes the UDP and TCP sockets to free network resources.

        Example:
            >>> NMS_server(storage_path).close()
        """

        self._stop_event.set()
        self.threads[0].join()
        self.UDP_socket.close()
        self.TCP_socket.close()

    def handle_client(self , conn, addr):
        """
        Handles communication with a single client over a TCP connection.

        This function receives data from the client, processes it based on the message type, 
        and performs specific actions, such as opening or writing to a file. It maintains 
        an open connection to the client, receiving and handling data until the connection is closed.

        Behavior:
            - Receives data in chunks of 1024 bytes from the connected client.
            - Parses the message to identify the message type.
            - If the message type is `1`, it splits the decoded data and opens a file based on the provided information.
            - If the message type is not `1`, it writes the decoded data (e.g., alert information) to the open file.
            - Continues to listen for incoming data until the connection is closed by the client.

        Args:
            conn (socket.socket): The socket object representing the connection with the client.
            addr (tuple): The address (IP and port) of the connected client.

        Raises:
            IOError: If an error occurs while reading from or writing to the file.

        Example:
            >>> NMS_server(storage_path).handle_client(conn, addr)
        """

        #print('Connected by', addr)
        file = None
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                 break
                headers = data[:2]
                messageType = struct.unpack('!H',headers)

                decoded_data = data[2:].decode('utf-8')
                #print(f'Aqui está a message tpye: {messageType}')

                if messageType[0] == 1:
                    #print(f'Aqui está a decoded data: {decoded_data}')
                    info = decoded_data.split()
                    file = openFile(info[0], info[1], self.storage_path)
                else:
                    #print(f'Aqui está a decoded data: {decoded_data}')
                    file.write(f"AlertFlow: {decoded_data}\n")
                    file.flush()

        #print(f"Connection with {addr} closed.")

    def listen_TCP(self, socket):
        """
        Listens for incoming TCP connections and handles client communication.

        This function listens for incoming TCP connections on the specified socket. 
        When a new connection is accepted, it starts a new thread to handle the communication 
        with the connected client by calling `handle_client`.

        Behavior:
            - Listens for incoming connections on the TCP socket.
            - When a client connects, accepts the connection and starts a new thread.
            - Each thread handles client communication using the `handle_client` method.

        Args:
            socket (socket.socket): The TCP socket used to listen for incoming connections.

        Example:
            >>> NMS_server(storage_path).listen_TCP(socket)
        """

        #s.listen()
        self.TCP_socket.listen()
        
        #print(f"TCP a ouvir")
        while True:
            conn, addr = self.TCP_socket.accept()
            # Start a new thread to handle the client
            client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            client_thread.daemon = True  # Ensures threads close when the main program exits
            client_thread.start()
