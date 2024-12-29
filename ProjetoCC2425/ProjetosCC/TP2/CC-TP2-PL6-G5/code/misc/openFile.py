import os

def openFile(task_id, device_id, storage_path):
        
        """
        Opens a file for writing, creating necessary directories if they don't exist.

        This function ensures that the specified storage path and task directory exist. 
        If they don't, it creates them. It then opens (or creates if not already present) 
        a text file named after the device ID and returns the file object for writing.

        Behavior:
            - Checks if the provided `storage_path` exists; if not, creates it.
            - Creates a task-specific directory for the given `task_id` within the `storage_path`.
            - Opens a text file named after the `device_id` in append mode (`"a"`), or creates it if not present.
            - Returns the file object, allowing further writing to the file.

        Args:
            task_id (int): The task ID used to create a specific directory for the task.
            device_id (str): The device ID used as the name of the file (with a `.txt` extension).
            storage_path (str): The base directory where task-specific folders and files will be stored.

        Returns:
            file: The opened file object for the specific device ID, ready for writing.

        Raises:
            OSError: If an error occurs while creating directories or opening the file.

        Example:
            >>> file = openFile(1, "device1", "/path/to/storage")
            >>> file.write("Some data\n")
            >>> file.close()
        """

        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
        

        task_dir = os.path.join(storage_path, str(task_id))
        if not os.path.exists(task_dir):
            os.makedirs(task_dir)

        file_name = f"{device_id}.txt"
        file_path = os.path.join(task_dir, file_name)

        file = open(file_path, "a")
        return file