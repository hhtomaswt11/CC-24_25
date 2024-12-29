class ClientServer:
    """
    A class that represents a client server, which holds information about a client,
    its associated socket, and its metrics.

    Attributes:
        `address` (str): The IP address or identifier of the client server.
        `socket` (socket): The socket object representing the connection to the client server.
        `metrics` (dict): A dictionary that stores metrics related to the client by task ID.

    Methods:
        `__init__`: Initializes a new instance of the ClientServer class.
        `to_dict`: Converts the client server's information into a dictionary.
        `add_metric`: Adds a metric for a specific task to the client's metrics dictionary.
    """

    def __init__(self, addr, socket):
        """
        Initializes a new instance of the ClientServer class.

        Args:
            `addr` (str): The IP address or identifier of the client server.
            `socket` (socket): The socket object representing the connection to the client server.
        """
        self.address = addr
        self.socket = socket
        self.metrics = {}

    def to_dict(self):
        """
        Converts the client server's information into a dictionary.

        Returns:
            `dict`: A dictionary containing the address, socket, and metrics of the client server.
        """
        return {
            "address": self.address,
            "socket": self.socket,
            "metrics": self.metrics
        }
    
    def add_metric(self, task_id: str, metric: str):
        """
        Adds a metric for a specific task to the client's metrics dictionary. 
        If the task ID already has metrics, the new metric is appended to the existing metrics.

        Args:
            `task_id` (str): The unique identifier for the task.
            `metric` (str): The metric associated with the task to be added.

        Note:
            If the task ID already exists in the metrics dictionary, this method will append the new metric
            to the existing value. If it doesn't exist, it will create a new entry for that task ID.
        """
        if task_id not in self.metrics:
            self.metrics[task_id] = metric
        else:
            self.metrics[task_id] += ", " + metric  # Append the new metric
