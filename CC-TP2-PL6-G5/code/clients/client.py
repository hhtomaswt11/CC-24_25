import json
import socket
import struct
import uuid
from tasks.config import AlertflowConditions
from tasks.parser import parseTasks
from tasks.task import Task
from misc.sendMessage import sendMessage
import threading
import time
import random
import subprocess
import psutil
import shlex
import os
from datetime import datetime
import re

class Client: 
    """
    A class representing a network client that communicates with a server using both UDP and TCP sockets.

    Attributes:
        `id` (str): The unique identifier for the client, either provided or automatically generated.
        `server_ip` (str): The IP address of the server to communicate with.
        `server_port` (int): The port number on which the server listens.
        `UDP_socket` (socket.socket): The UDP socket used for communication with the server.
        `TCP_socket` (socket.socket): The TCP socket used for communication with the server.
        `Tasks` (list): A list to store the tasks associated with the client.
        `connected` (bool): Flag indicating whether the client is connected to the server.
        `lock` (threading.Lock): A lock for thread safety.
        `_stop_event` (threading.Event): An event used to signal when to stop the client.
        `sequences` (dict): A dictionary for storing message sequences.
        `sequence` (int): A counter for the current message sequence.
        `doingTask` (bool): A flag indicating whether the client is performing a task.
    """

    def __init__(self, server_ip: str, server_port: int, client_id: str = None):
        """
        Initializes a new instance of the Client class.

        This constructor sets up the initial state of the client, including its unique ID,
        server connection details (IP and port), and necessary socket objects for communication.
        The method also initializes the task list, the lock for thread synchronization, and 
        other internal flags such as connection status and task management.

        Args:
            `server_ip` (str): The IP address of the server the client will communicate with.
            `server_port` (int): The port number of the server for communication.
            `client_id` (str, optional): A unique identifier for the client. If not provided,
                                       a random UUID will be generated.

        Attributes:
            `id` (str): A unique identifier for the client. If `client_id` is not provided, a random UUID is generated.
            `server_ip` (str): The server's IP address.
            `server_port` (int): The server's port number.
            `UDP_socket` (socket.socket): The UDP socket for communication.
            `TCP_socket` (socket.socket): The TCP socket for communication (created only when necessary).
            `Tasks` (list): A list of tasks assigned to the client.
            `connected` (bool): Flag indicating the connection status with the server.
            `lock` (threading.Lock): A threading lock for ensuring thread safety.
            `_stop_event` (threading.Event): An event used to signal when to stop the client.
            `sequences` (dict): Dictionary to manage message sequences.
            `sequence` (int): The current sequence number for messages.
            `doingTask` (bool): Flag indicating if the client is currently performing a task.
        """
        # Se o client_id não for fornecido, gera um ID aleatório
        self.id = client_id if client_id else str(uuid.uuid4())
        self.server_ip = server_ip
        self.server_port = server_port
        self.UDP_socket = self.setup_UDP_socket()
        self.TCP_socket = self.setup_TCP_socket()  # socket TCP só é criado quando necessário
        self.Tasks = []
        self.connected = False
        self.lock = threading.Lock()
        self._stop_event = threading.Event()
        self.sequences = {}
        self.sequence = 0
        self.doingTask = False





    def setup_UDP_socket(self):
        """
        Sets up and returns a UDP socket bound to a random available port.

        This function creates a UDP socket using the IPv4 address family and the UDP protocol. 
        It binds the socket to a local address, allowing it to listen for incoming UDP packets 
        on a randomly selected port between 1 and 65535.

        Behavior:
            - Creates a UDP socket using `AF_INET` (IPv4) and `SOCK_DGRAM` (UDP).
            - Binds the socket to all available network interfaces (`'0.0.0.0'`) and a randomly 
            selected port number between 1 and 65535.
            - Returns the created and bound UDP socket.

        Returns:
            socket.socket: The created UDP socket bound to the randomly selected port.

        Raises:
            OSError: If there is an error creating or binding the socket.

        Example:
            >>> udp_socket = Client().setup_UDP_socket()
            >>> print(udp_socket)
        """

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('0.0.0.0', random.randint(1, 65535)))
        return udp_socket

    def setup_TCP_socket(self):
        """
        Sets up and returns a TCP socket bound to a random available port.

        This function creates a TCP socket using the IPv4 address family and the TCP protocol. 
        It binds the socket to a local address, allowing it to listen for incoming TCP connections 
        on a randomly selected port between 1 and 65535.

        Behavior:
            - Creates a TCP socket using `AF_INET` (IPv4) and `SOCK_STREAM` (TCP).
            - Binds the socket to all available network interfaces (`'0.0.0.0'`) and a randomly 
            selected port number between 1 and 65535.
            - Returns the created and bound TCP socket.

        Returns:
            `socket.socket`: The created TCP socket bound to the randomly selected port.

        Raises:
            `OSError`: If there is an error creating or binding the socket.

        Example:
            >>> tcp_socket = Client().setup_TCP_socket()
            >>> print(tcp_socket)
        """

        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind(('0.0.0.0', random.randint(1, 65535)))
        return tcp_socket
    

    def send_initial_info(self):
        """
        Sends initial connection information to the server over UDP.

        This function repeatedly sends the client’s ID to the server in a UDP datagram until 
        a successful connection is established or a stop event is triggered. The message 
        is sent every 5 seconds while the client is not connected.

        Behavior:
            - Continuously sends the client ID to the server using the `sendMessage` function.
            - The message is sent to the server's IP address and port over a UDP connection.
            - Repeats the sending every 5 seconds until the client is connected or the stop event occurs.

        Example:
            >>> Client().send_initial_info()
        """

        while self.connected == False and not self._stop_event.is_set():
            # Send this message to the server over UDP
                sendMessage(self.UDP_socket, (self.server_ip, self.server_port), self.id, 0)
                time.sleep(5)
           


    def listen_for_datagrams(self):
        """
        Listens for incoming UDP datagrams and processes them.

        This function continuously listens for incoming UDP datagrams on the bound socket. 
        When a datagram is received, it is passed to the `handle_datagram` function for further processing. 
        The listening loop will terminate if a stop event is triggered or if a connection error occurs.

        Behavior:
            - Continuously listens for UDP datagrams on the socket.
            - When a datagram is received, the data is passed to `handle_datagram` for processing.
            - If a `ConnectionResetError` or `OSError` occurs, the loop exits.

        Example:
            >>> Client().listen_for_datagrams()
        """

        buffer_size = 1024
        while not self._stop_event.is_set():
            try:
                #print(f"Client listening:\n")
                data, addr = self.UDP_socket.recvfrom(buffer_size)
                if data:
                    self.handle_datagram(data, addr)
            except ConnectionResetError as e:
                #print(f"Connection reset error: {e}")
                break
            except OSError as e:
                #print(f"OS error (likely socket issue): {e}")
                break

    def executeTask(self, command:str):
        """
        Executes a system command and sends the output or error message via UDP.

        This function executes a system command using the `subprocess.run` method. It splits the 
        command string safely into arguments, runs the command, and captures its output or error 
        messages. The result is then sent to the server over UDP.

        The function ensures that the task is executed without interference by using a lock to 
        synchronize access to shared resources. If any exception occurs during the execution, 
        an error message is sent instead.

        Behavior:
            - Acquires a lock to indicate that a task is being executed.
            - Safely splits the command string and executes the system command.
            - Captures the command's standard output and error.
            - Sends the output or error message to the server via UDP (using the `sendMessage` function).
            - Releases the lock once the task is completed.
            - In case of an error, an error message is sent via UDP.

        Args:
            `command` (str): The system command to be executed.

        Raises:
            `Exception`: If an unexpected error occurs during the execution of the command.

        Example:
            >>> Client().executeTask("ls -l")
        """

        with self.lock:
            self.doingTask = True
        try:
            # Split the command safely
            args = shlex.split(command)
        
        # Execute the command and capture output
            response = subprocess.run(args, capture_output=True, text=True)
        
        # Check for errors
            if response.returncode != 0:
                output = f"Error: {response.stderr}"
            else:
                output = response.stdout
        
        # Send the response via UDP
            #time.sleep(5)
            output = response.stdout
            with self.lock:
                self.doingTask = False

                #print ("TCP SOCKET FECHADA")
                
            sendMessage(self.UDP_socket, (self.server_ip, self.server_port), output, 2)
            with self.lock:
                self.doingTask = False
    
    
        except Exception as e:
        # Handle unexpected exceptions
            error_message = f"An error occurred: {str(e)}"
            sendMessage(self.UDP_socket, (self.server_ip, self.server_port), error_message, 2)


    
    def alert_conditions(self,alertFlowConditions: AlertflowConditions,cpu_percentage_usage: float, ram_percentage_usage: float, interface, packet_loss, jitter):
        """
        Checks if any of the alert conditions are met based on the provided parameters.

        This function evaluates whether the provided system metrics (CPU usage, RAM usage, 
        packet loss, jitter) or network interface statistics exceed the defined thresholds 
        in the `alertFlowConditions`. If any of the conditions are met, it returns `True`, 
        indicating that an alert condition is triggered. Otherwise, it returns `False`.

        Behavior:
            - Compares the given CPU and RAM usage, packet loss, and jitter against 
            their respective thresholds from `alertFlowConditions`.
            - If any of these parameters exceed the defined thresholds, the function 
            returns `True`.
            - Additionally, it checks if any of the network interface stats exceed 
            the defined limits. If any condition is met, it returns `True`.
            - If no conditions are met, it returns `False`.

        Args:
            `alertFlowConditions` (AlertflowConditions): The object containing the alert thresholds 
                                                    for CPU, RAM, packet loss, jitter, and interface stats.
            `cpu_percentage_usage` (float): The current CPU usage percentage to compare against the threshold.
            `ram_percentage_usage` (float): The current RAM usage percentage to compare against the threshold.
            `interface` (list): A list of network interface statistics, where each entry is a tuple with 
                            two values to be compared against the `interface_stats` threshold.
            `packet_loss` (float): The current packet loss percentage to compare against the threshold.
            `jitter` (float): The current jitter value to compare against the threshold.

        Returns:
            `bool`: `True` if any alert condition is met, otherwise `False`.

        Example:
            >>> Client().alert_conditions(alertFlowConditions, 85.0, 75.0, interface_stats, 2.0, 10.5)
        """

        if(alertFlowConditions.cpu_usage <= cpu_percentage_usage or alertFlowConditions.ram_usage <= ram_percentage_usage or alertFlowConditions.packet_loss <= packet_loss or alertFlowConditions.jitter_limit <= jitter):
            return True
        else:
            for i in interface:
                if alertFlowConditions.interface_stats <= i[0] or alertFlowConditions.interface_stats <= i[1]:
                    return True 
            return False

    def medir(self, task: Task):
        """
        Measures and collects system and network performance metrics based on the provided task configuration.

        This function monitors the CPU usage, RAM usage, bandwidth, latency, jitter, and packet loss for the 
        duration of the task, collecting data at the specified frequency. The metrics are gathered and compiled 
        into a message that is then sent to the server.

        The function performs the following:
            - Measures CPU and RAM usage, based on the task's configuration.
            - Measures bandwidth using `iperf` by connecting to a server.
            - Measures latency, jitter, and packet loss by pinging the server.
            - Sends the collected data as a message to the server over UDP.

        Args:
            `task` (Task): The task object that contains the configuration settings for the metrics to be measured.
                        The task includes details such as the frequency and duration of measurements, and the 
                        configuration for device metrics (CPU, RAM) and link metrics (bandwidth, latency, jitter, packet loss).

        Returns:
            `None`: The function sends the measured metrics as a message to the server.

        Example:
            >>> task = Task()
            >>> Client().medir(task)
        """

        task_id = task.task_id
        frequency = task.frequency
        duration = task.duration
        cpu = 0
        ram = 0
        message_parts = []

        for i in range(0,int(duration/frequency)):
            message_parts = []
            if task.config.device_metrics.cpu_usage:
             cpu = psutil.cpu_percent(interval=0)
            if task.config.device_metrics.ram_usage:
             ram = psutil.virtual_memory().percent
            for j in range(1,frequency):
                if cpu != 0:
                    cpu = cpu + psutil.cpu_percent(interval=0)
                if ram != 0:
                    ram = ram + psutil.virtual_memory().percent
                time.sleep(1)

            if task.config.device_metrics.cpu_usage:
               message_parts.append(f"cpu_usage: {(cpu/(frequency+1))}%")
            if task.config.device_metrics.ram_usage:
               message_parts.append(f"ram_usage: {(ram/(frequency+1))}%")

            if task.config.link_metrics.bandwidth:
                server_addr = task.config.link_metrics.server_address
                result = subprocess.run(["iperf", "-c", server_addr, "-t", "1", "-f", "g"], capture_output=True, text=True)

                if result.returncode == 0:
                # Procure pela linha que contém as informações de largura de banda usando regex
                  #print(result.stdout)#.decode('utf-8'))
                  match = re.search(r"(\d+\sGBytes)\s+(\d+.\d+\sGbits/sec)", result.stdout)
                  if match:
                     transfer = match.group(1)  # Ex: "798 MBytes"
                     bandwidth = match.group(2).split()  # Ex: "6.66 Mbits/sec"
                     
                     bandwidth_mbps = float(bandwidth[0]) * 1000
                     message_parts.append(f"bandwidth: {bandwidth_mbps}Mbps") 

            if task.config.link_metrics.latency.latency or task.config.link_metrics.jitter or task.config.link_metrics.packet_loss:
               server_addr = task.config.link_metrics.server_address
               packet_count = str(task.config.link_metrics.latency.packet_count) 
               result = subprocess.run(["ping", server_addr, "-c", packet_count], capture_output=True, text=True)

               if result.returncode == 0:
                 # Procure pelas estatísticas de RTT (min, avg, max, mdev)
                 rtt_match = re.search(r"min/avg/max/mdev = (\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)", result.stdout)

                 loss_match = re.search(r"(\d+)% packet loss", result.stdout)

                 if rtt_match and loss_match:
                  # Extraia os valores de RTT
                  min_rtt = float(rtt_match.group(1))
                  avg_rtt = float(rtt_match.group(2))
                  max_rtt = float(rtt_match.group(3))
                  mdev_rtt = float(rtt_match.group(4))

                  packet_loss = float(loss_match.group(1))
                  if task.config.link_metrics.latency.latency:
                        message_parts.append(f"Latency: {avg_rtt}ms")                      
                  if task.config.link_metrics.jitter: 
                        jitter = max_rtt - min_rtt  
                        message_parts.append(f"Jitter: {jitter} ms")
                  if task.config.link_metrics.packet_loss:   
                        message_parts.append(f"Packet_loss: {(packet_loss)}%")


            if message_parts:
                message = " ".join(message_parts)
                #print(f"Mensagem: {message}")
                sendMessage(self.UDP_socket, (self.server_ip, self.server_port), message, 3)
        
    
    def alertFlow(self, task: Task):
        """
        Monitors and sends periodic alerts related to system metrics and network performance based on the task configuration.

        This function continuously monitors system metrics such as CPU usage, RAM usage, and network interface statistics 
        (packets sent/received) as well as network performance metrics like packet loss and jitter. If any of the monitored 
        metrics exceed the defined thresholds (based on alert conditions in the task configuration), an alert message is 
        generated and sent to the server via the TCP socket.

        The alert messages are sent in a specific format, containing:
            - CPU and RAM usage
            - Network interface statistics (sent/received packets)
            - Packet loss and jitter
            - Time of the alert

        The function keeps polling the system and network metrics until the task is completed or an error occurs.

        Args:
            `task` (Task): The task object that contains the configuration settings for monitoring and alert generation, 
                        including device metrics (CPU, RAM, network interfaces) and link metrics (packet loss, jitter). 
                        It also defines alert thresholds for the conditions.

        Returns:
            `None`: This function sends alert notifications to the server but does not return any value.

        Example:
            >>> task = Task() 
            >>> Client().alertFlow(task)
        """

        message = struct.pack('!H', 1) + task.task_id.encode('utf-8') + b" " + self.id.encode('utf-8') + b'\n'
        self.TCP_socket.sendall(message)

        while self.doingTask:
            packet_loss = 0
            jitter = 0
            cpu = psutil.cpu_percent(interval=1)  
            ram = psutil.virtual_memory().percent
            interface = []
            for i in task.config.device_metrics.interface_stats:
                    net1 = psutil.net_io_counters(pernic=True)[i]
                    packets_sent_1 = net1.packets_sent
                    packets_recv_1 = net1.packets_recv

                    time.sleep(1)

                    net2 = psutil.net_io_counters(pernic=True)[i]
                    packets_sent_2 = net2.packets_sent
                    packets_recv_2 = net2.packets_recv

                    pps_sent = (packets_sent_2 - packets_sent_1)
                    pps_recv = (packets_recv_2 - packets_recv_1)

                    interface.append((pps_sent, pps_recv))
            result = subprocess.run(["ping", task.config.link_metrics.server_address, "-c", "2"], capture_output=True, text=True)
            if result.returncode == 0:
                 # Procure pelas estatÃ­sticas de RTT (min, avg, max, mdev)
                 rtt_match = re.search(r"min/avg/max/mdev = (\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)", result.stdout)

                 loss_match = re.search(r"(\d+)% packet loss", result.stdout)

                 if rtt_match and loss_match:
                  # Extraia os valores de RTT
                  min_rtt = float(rtt_match.group(1))
                  avg_rtt = float(rtt_match.group(2))
                  max_rtt = float(rtt_match.group(3))
                  mdev_rtt = float(rtt_match.group(4))

                  packet_loss = float(loss_match.group(1))
                  jitter = max_rtt - min_rtt
            send_alert_notification = self.alert_conditions(task.config.alertflow_conditions, cpu, ram, interface, packet_loss, jitter)

            if send_alert_notification:
                current_time = str(datetime.now())
                try:
                    cpu_string ="cpu_alert_condition: " +  str(task.config.alertflow_conditions.cpu_usage)  + "% | cpu_usage: " + str(cpu) + "%"
                    ram_string ="ram_alert_condition: " +  str(task.config.alertflow_conditions.ram_usage)  + "% | ram_usage: " + str(ram) + "%"
                    interface_string = "interface_stats_conditions: " + str(task.config.alertflow_conditions.interface_stats) + "pps | "
                    for i,j in zip(task.config.device_metrics.interface_stats, interface):
                        interface_string = interface_string + i + ": sent-" + str(j[0]) + "pps receive-" + str(j[1]) + "pps"
                    packet_loss_string = "packet_loss_condition: " + str(task.config.alertflow_conditions.packet_loss) + "% | packet_loss: " + str(packet_loss) + "%"
                    jitter_string = "jitter_condition: " + str(task.config.alertflow_conditions.jitter_limit) + "ms | jitter: " + str(jitter) + "ms"
                    message = struct.pack('!H', 2) + current_time.encode('utf-8') + b'\n' + cpu_string.encode('utf-8') + b'\n' + ram_string.encode('utf-8') + b'\n' + interface_string.encode('utf-8') + b'\n' + packet_loss_string.encode('utf-8') + b'\n' + jitter_string.encode('utf-8') + b'\n'
                    self.TCP_socket.sendall(message)
                except socket.error as e:
                    #print(f"Socket send error: {e}")
                    break  # stop further attempts on errors
            time.sleep(1)  # Avoid overloading resource polling
        self.TCP_socket.close()
        self.TCP_socket = self.setup_TCP_socket()






    def parseTask(self, sequenceLength):
        """
        Parses a task from a JSON string and initiates task execution along with monitoring and Alertflow.

        This function takes a sequence of task data, parses it into a Python dictionary, extracts the task details, 
        and initiates the task execution process. It also starts threads for monitoring and Alertflow if the task 
        configuration defines alert conditions.

        The function performs the following steps:
            1. Combines task sequences into a single JSON string.
            2. Converts the JSON string into a Python dictionary.
            3. Parses the task details and creates a Task object using the task ID.
            4. If the task has Alertflow conditions defined, establishes a TCP connection to the server.
            5. Starts the execution thread to run the task.
            6. If Alertflow conditions are set, starts a separate thread for monitoring the task and sending alerts.
            7. Calls the `medir` function to monitor and collect task metrics.

        Args:
            `sequenceLength` (int): The number of sequences to combine and parse into a single task.

        Returns:
            `None`: The function starts threads for task execution and Alertflow but does not return any value.

        Example:
            >>> Client().parseTask(5)
        """

        taskList = self.sequences[0]
        for i in range(1,sequenceLength):
            taskList += self.sequences[i] 
        # Converte a string JSON para um dicionário Python
        taskDict = json.loads(taskList)

        # Parse taskString to Task
        taskId = taskDict["task_id"]
        taskObject = parseTasks(taskId[2:], taskDict)

        #print(taskObject.to_bytes())
        if taskObject.config.alertflow_conditions.alertflow_conditions:
            self.TCP_socket.connect((self.server_ip, 54322))

        # Inicia as threads necessárias
        exec_thread = threading.Thread(target=self.executeTask, args=(taskObject.type,))
        exec_thread.daemon = True
        exec_thread.start()

        if taskObject.config.alertflow_conditions.alertflow_conditions:
            alert_thread = threading.Thread(target=self.alertFlow, args=(taskObject,))
            alert_thread.daemon = True
            alert_thread.start()

        self.medir(taskObject)

        """
        medir_thread = threading.Thread(target=self.medir, args=(taskObject,))
        medir_thread.daemon = True
        medir_thread.start()
        """

        #return "".join(taskList)

    def do_iperf(self, duration):
        """
        Starts an iperf3 server to measure network performance for a specified duration.

        This function sets up and runs an iperf3 server using the `subprocess.run` method. 
        The server runs for the duration specified by the `duration` argument, 
        and it will listen for incoming connections to perform network performance testing.

        The function runs the iperf3 server in blocking mode, meaning it will not return control to the program 
        until the server is manually interrupted or the specified duration ends. If an error occurs while 
        starting the server, an error message will be printed.

        Args:
            `duration` (int): The duration in seconds for which the iperf3 server should run.

        Returns:
            `None`: The function does not return any value but starts the iperf3 server as a blocking process.

        Example:
            >>> Client().do_iperf(60)
        """

        command = ["iperf", "-s", "-t", duration]

        # Start the iperf3 server using subprocess.run
        try:
            # Running the iperf3 server in blocking mode (it will run until interrupted)
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(" ")




    def handle_datagram(self,data, addr):
        """
        Handles incoming datagrams and processes them based on the message type and sequence information.

        This function is responsible for decoding and processing incoming UDP datagrams. 
        It handles different types of messages based on the `messageType` field in the received datagram. 
        Specifically, it:
            - Parses the received data to extract the relevant message content.
            - Processes the datagram based on its message type (e.g., `0`, `1`, or `4`).
            - Manages a sequence of datagrams for larger message payloads, ensuring that all parts are received before processing.
            - Sends acknowledgment messages when appropriate and spawns necessary threads for task execution.

        Args:
            `data` (bytes): The received datagram in byte format, which includes headers and payload.
            `addr` (tuple): The address (IP, port) of the sender, used for sending responses.

        Returns:
            `None`: The function does not return any value but performs processing and manages internal state.

        Message Types:
            - `0`: Used for setting the server's port (establishing a connection).
            - `1`: Used for receiving parts of a task or sequence and processing it when fully received.
            - `4`: Triggers an iperf test based on the provided payload.
            - `5`: Resets the sequence state, preparing for new message processing.

        Example:
            >>> Client().handle_datagram(data, addr)
        """

        # Decodifique os dados recebidos de bytes para string
        payload = data[14:]
        payload = payload.decode('utf-8')  # 'ignore' skips invalid bytes
        headers = data[:10]
        sequence = data[10:14]
        source_port, dest_port, length, checksum, messageType = struct.unpack('!HHHHH', headers)
        sequence_number, sequence_length = struct.unpack('!HH', sequence)

        if messageType == 5:
          self.sequences = {}
          self.sequence = 0
          messageType = 1
       
          #print(f"Adrr: {addr}\n")

        
        # Verifique se a mensagem contém um ID para processar os dados do cliente
        if messageType == 0:


            # Obtenha os dados do cliente e valide se todos os campos estão presentes
            with self.lock:        
                self.server_port = int(payload)
                #print(str(self.server_port)+" here")
                self.connected = True

        else:
            if messageType == 1:
                
                if sequence_number not in self.sequences: 
                    self.sequences[sequence_number] = payload            
               
                #self.sequences[sequence_number] = payload
                    self.sequence += 1
                if self.sequence == sequence_length:
                    self.parseTask(sequence_length)
                    #print(taskString)
                    
                    self.sequence = 0
                    self.sequences = {}
                    # Enviar Ack para o servidor
                    sendMessage(self.UDP_socket, (self.server_ip, self.server_port),"Received", 1)

                    # Criar Threads no cliente : Metrics Thread, AlertFlow Thread , Execute Task Thread

                    # Execute Task
            else:
                if messageType == 4:
                    iperf_thread = threading.Thread(target=self.do_iperf, args=(payload,))
                    iperf_thread.daemon = True
                    iperf_thread.start()
                    #self.do_iperf(payload)


    def to_dict(self):
        """
        Converts the client object data into a dictionary format.

        This method converts the client object's attributes (`id`, `server_ip`, `server_port`, and `Tasks`) into a dictionary 
        representation. This can be useful for serialization, logging, or transmitting the client's data in a structured format.

        Returns:
            dict: A dictionary containing the client's data with the following keys:
                - "`id`": The client's unique identifier.
                - "`server_ip`": The server's IP address that the client is connected to.
                - "`server_port`": The server's port that the client is using.
                - "`Tasks`": The list or dictionary of tasks associated with the client.

        Example:
            >>> client = Client(id="123", server_ip="192.168.1.1", server_port=8080, Tasks=[])
            >>> client_dict = client.to_dict()
            >>> print(client_dict)
            {'id': '123', 'server_ip': '192.168.1.1', 'server_port': 8080, 'Tasks': []}
        """

        return {
            "id": self.id,
            "server_ip": self.server_ip,
            "server_port": self.server_port,
            "Tasks": self.Tasks
        }

    def close(self):
        """
        Closes the UDP socket and sets the stop event to signal termination.

        This method performs the following actions:
        1. Closes the UDP socket to terminate communication.
        2. Sets the stop event flag (`_stop_event`) to indicate that the process or thread should stop.
        
        The `with self.lock:` block ensures that these actions are performed atomically, preventing race conditions 
        in a multi-threaded environment.

        Note:
            This method should be called to gracefully shut down the network communication and any ongoing operations 
            associated with the UDP socket.

        Example:
            >>> client = Client()
            >>> client.close()
        """

        with self.lock:
            self.UDP_socket.close()
            self._stop_event.set()
            # Close the socket
