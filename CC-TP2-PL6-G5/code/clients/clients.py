import json
from .client_server import ClientServer

class Clients:
    """
    A class that manages a collection of ClientServer instances.

    This class is designed to store and manage clients identified by unique IDs.
    It allows adding, removing, retrieving, and listing clients. Additionally, it supports 
    converting the list of clients to a dictionary or JSON representation.

    Attributes:
        `clients` (dict): A dictionary where the keys are client IDs and the values are ClientServer instances.

    Methods:
        `__len__`: Returns the number of clients in the collection.
        `add_client`: Adds a new client to the collection with a given ID.
        `remove_client`: Removes a client from the collection by its ID.
        `get_client`: Retrieves a client from the collection by its ID.
        `to_dict`: Converts the collection of clients into a dictionary representation.
        `__str__`: Returns a JSON-formatted string representation of the clients collection.
        `__iter__`: Returns an iterator for iterating over the clients.
        `get_client_ids`: Returns a list of all client IDs in the collection.
        `at_least_one`: Checks if at least one of the given devices exists in the client collection.
    """

    def __init__(self):
        """
        Initializes a new instance of the Clients class.

        The constructor sets up an empty dictionary to store client objects.

        Attributes:
            `clients` (dict): A dictionary that stores clients by their unique IDs.
        """
        self.clients = {}

    def __len__(self):
        """
        Returns the number of clients in the collection.

        Returns:
            `int`: The number of clients stored in the `clients` dictionary.
        """
        return len(self.clients)

    def add_client(self, id, client: ClientServer):
        """
        Adds a client to the collection.

        Args:
            `id` (str): The unique ID of the client to be added.
            `client` (ClientServer): The ClientServer instance to be added to the collection.
        """
        self.clients[id] = client

    def remove_client(self, id: str):
        """
        Removes a client from the collection by its ID.

        Args:
            `id` (str): The unique ID of the client to be removed.
        """
        if id in self.clients:
            del self.clients[id]

    def get_client(self, id: str) -> ClientServer:
        """
        Retrieves a client from the collection by its ID.

        Args:
            `id` (str): The unique ID of the client to be retrieved.

        Returns:
            `ClientServer`: The client corresponding to the provided ID, or None if not found.
        """
        return self.clients.get(id)

    def to_dict(self):
        """
        Converts the collection of clients to a dictionary representation.

        Returns:
            `dict`: A dictionary where keys are client IDs and values are the dictionary representation
                  of the associated `ClientServer` instances.
        """
        return {id: client.to_dict() for id, client in self.clients.items()}

    def __str__(self):
        """
        Returns a JSON-formatted string representation of the clients collection.

        Returns:
            `str`: A string containing a JSON-formatted representation of the client collection.
        """
        return json.dumps(self.to_dict(), indent=4)

    def __iter__(self):
        """
        Returns an iterator for iterating over the clients.

        Returns:
            `iterator`: An iterator over the items in the `clients` dictionary.
        """
        return iter(self.clients.items())

    def get_client_ids(self):
        """
        Returns a list of all client IDs in the collection.

        Returns:
            `list`: A list of all the client IDs stored in the collection.
        """
        return list(self.clients.keys())

    def at_least_one(self, devices):
        """
        Checks if at least one of the given devices exists in the client collection.

        Args:
            `devices` (list): A list of device IDs to check.

        Returns:
            `bool`: True if at least one device from the list exists in the collection, False otherwise.
        """
        for d in devices:
            client = self.get_client(d)
            if client:
                return True
        return False
