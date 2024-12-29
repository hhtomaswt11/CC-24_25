import json
from .task import Task


class Tasks:
    """
    A class to manage a collection of tasks, allowing adding, removing, and accessing tasks by their IDs.
    It also provides functionality to serialize tasks into dictionaries or JSON format.

    Attributes:
        `tasks` (dict): A dictionary that stores the tasks, with task IDs as keys and Task objects as values.
    """
    
    def __init__(self):
        """
        Initializes the collection of tasks as an empty dictionary.
        """
        self.tasks = {}

    def add_task(self, task: Task):
        """
        Adds a new task to the task collection.

        Args:
            `task` (Task): The Task object to be added to the collection.
        """
        self.tasks[task.task_id] = task

    def remove_task(self, task_id: str):
        """
        Removes a task from the task collection based on the provided ID.

        Args:
            `task_id` (str): The ID of the task to be removed.
        
        If the task ID does not exist, nothing happens.
        """
        if task_id in self.tasks:
            del self.tasks[task_id]

    def get_task(self, task_id: str) -> Task:
        """
        Retrieves a task by its ID.

        Args:
            `task_id` (str): The ID of the task to be retrieved.
        
        Returns:
            `Task`: The Task object associated with the provided ID. Returns `None` if no task with that ID exists.
        """
        return self.tasks.get('T-' + str(task_id))
    
    def to_dict(self):
        """
        Converts all tasks in the collection into a dictionary, facilitating JSON serialization.

        Returns:
            `dict`: A dictionary where the keys are task IDs and the values are the task representations in dictionary format.
        """
        return {task_id: task.to_dict() for task_id, task in self.tasks.items()}
    
    def __str__(self):
        """
        Converts the task collection into a formatted JSON string for easy readability.

        Returns:
            `str`: The string representation of the tasks in JSON format.
        """
        return json.dumps(self.to_dict(), indent=4)

    def __len__(self):
        """
        Returns the total number of tasks in the collection.

        Returns:
            `int`: The number of tasks stored in the collection.
        """
        return len(self.tasks)
