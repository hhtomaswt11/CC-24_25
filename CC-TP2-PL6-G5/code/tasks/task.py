from dataclasses import dataclass
import pickle
from typing import List, Dict
import json

from tasks.config import Config


@dataclass
class Task:
    """
    A class representing a Task with relevant properties like type, frequency, duration, 
    associated devices, and configuration details.
    
    Attributes:
        `task_id` (str): Unique identifier for the task.
        `type` (str): Type of the task (e.g., 'ping', 'iperf').
        `frequency` (int): The frequency at which the task should run.
        `duration` (int): The duration for which the task should run.
        `devices` (List[str]): List of device identifiers associated with the task.
        `config` (Config): Configuration object that holds specific metrics, link metrics, and alert flow conditions.
    """
    
    def __init__(self, id: int, type: str, frequency: int, duration: int, devices: List[str], config: Config):
        """
        Initializes a new instance of the Task class.
        
        Args:
            `id` (int): Task identifier.
            `type` (str): Type of the task (e.g., 'ping', 'iperf').
            `frequency` (int): Frequency at which the task will execute.
            `duration` (int): Duration for the task.
            `devices` (List[str]): List of device identifiers that the task involves.
            `config` (Config): Configuration object containing the device metrics and other settings for the task.
        """
        self.task_id = "T-" + str(id)
        self.type = type
        self.frequency = frequency
        self.duration = duration
        self.devices = devices
        self.config = config 

    def getDevices(self):
        """
        Retrieves the list of devices associated with this task.
        
        Returns:
            `List[str]`: A list of device identifiers.
        """
        return self.devices

    def to_dict(self):
        """
        Converts the Task instance into a dictionary format, including configuration details.
        
        Returns:
            `dict`: A dictionary representing the Task with task details and configuration.
        """
        return {
            "task_id": self.task_id,
            "type": self.type,
            "frequency": self.frequency,
            "duration": self.duration,
            "devices": self.devices,
            "Devices": self.config.to_dict()
        }

    def to_bytes(self):
        """
        Serializes the Task instance into a JSON byte string.
        
        Returns:
            `str`: A JSON string representing the Task instance.
        """
        return json.dumps(self.to_dict())
    
    def serialize(self):
        """
        Serializes the Task instance into binary format using pickle.
        
        Returns:
            `bytes`: A binary representation of the Task instance.
        """
        return pickle.dumps(self)
    
    @classmethod
    def deserialize(cls, data):
        """
        Deserializes binary data back into a Task instance using pickle.
        
        Args:
            `data` (bytes): The binary data representing a serialized Task instance.
        
        Returns:
            `Task`: A new Task instance reconstructed from the binary data.
        """
        return pickle.loads(data)
