import json
import os
import socket
import struct
import threading
from clients.client import Client
from tasks.config import Config, Device_metrics, AlertflowConditions, LatencyConfig, Link_metrics
from tasks.task import Task
from tasks.tasks import Tasks
from clients.clients import Clients
from clients.client_server import ClientServer
from misc.sendMessage import sendMessage
from misc.openFile import openFile
import random
import time

class NMS_server_UDP:

    def __init__(self, storage_path):
        self.maxT = 3
        self.currentT = 0
        self.threads = {}
        self.storage_path = storage_path



    def listen_for_datagrams(self, cond, device: Client, socket, addr, task: Task):
        buffer_size = 1024
        if self.currentT == self.maxT:
            cond.wait()
        self.currentT += 1
        sequence = 0
        received = False
        socket.settimeout(30)
        sendMessage(socket, addr, task.to_bytes(), 1)
        file =openFile(task.task_id, device, self.storage_path)

        sequences = {}

        
        while not received:
            try:
                data, addre = socket.recvfrom(buffer_size)

                if data:
                    payload = data[14:]
                    headers = data[:10]
                    seq = data[10:14]
                    source_port, dest_port, length, checksum, messageType = struct.unpack('!HHHHH', headers)
                    sequence_number, sequence_length = struct.unpack('!HH', seq)
                    #print(payload.decode('utf-8'))
                    if messageType == 3:
                        #print(f"\nMETRICS: {payload.decode('utf-8')}\n")
                        file.write(f"METRICS: {payload.decode('utf-8')}\n")
                        #print(payload)
                        file.flush()
                    else: 

                     if messageType == 2:
                        #print(f"\nRESULTS: {payload.decode('utf-8')}\n")

                        #sequences[sequence_number] = payload
                        if sequence_number not in sequences: 
                            sequences[sequence_number] = payload

                            sequence += 1
                
                    """    
                    else:
                        print(payload.decode('utf-8'))
                    """
                    #print(f"Sequence: {sequence}\n Sequence_length: {sequence_length}")


                    if sequence == sequence_length and messageType == 2:
                 
                        #print("\nALGUMA COISA\n")
                        print(f"\nTask {task.task_id} completed on device {device}\n")
                        result = sequences[0]
                        for i in range(1,sequence_length):
                          result += sequences[i]
                          
                        
                        file.write(f"RESULTS: {result.decode('utf-8')}\n")
                        file.flush() 
                        del self.threads[device]
                        self.currentT -=1
                        received = True

                        with cond:
                            cond.notify()
                    
            except Exception as e:
               if "timed out" in str(e).lower():
                sequences = {}

                #print(f"Timeout occured in {addr}!")
                sequence = 0
                sendMessage(socket, addr, task.to_bytes(), 5)
            except ConnectionResetError as e:
                #print(f"Connection reset error: {e}")
                break
            except OSError as e:
                #print(f"OS error (likely socket issue): {e}")
                break
            #finally:
                #break
