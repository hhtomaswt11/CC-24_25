from tasks.task import Task
from tasks.config import AlertflowConditions, Config, Device_metrics, LatencyConfig, Link_metrics

def parseTasks(lastTask, task):
    """
    Parses a task dictionary and converts it into a Task object with all necessary configurations 
    such as device metrics, link metrics, and alert flow conditions.
    
    Args:
        `lastTask` (str): The identifier or reference to the last task processed.
        `task` (dict): A dictionary containing the task data that includes devices metrics, 
                     link metrics, and alert flow conditions.
    
    Returns:
        `Task`: A Task object populated with the data from the task dictionary.
    """
    # Parse device metrics from the task dictionary
    device_metrics = Device_metrics(
        task["Devices"]["devices_metric"]["cpu_usage"],
        task["Devices"]["devices_metric"]["ram_usage"],
        task["Devices"]["devices_metric"]["interface_stats"]
    )

    # Parse latency configuration if it exists
    latency = task["Devices"]["link_metrics"]["latency"]
    if latency:
        latency_config = LatencyConfig(
            True,
            task["Devices"]["link_metrics"]["packet_count"]
        )
    else:
        latency_config = LatencyConfig()

    # Parse link metrics
    link_metrics = Link_metrics(
        task["Devices"]["link_metrics"]["use_iperf"],
        task["Devices"]["link_metrics"]["server"],
        task["Devices"]["link_metrics"]["duration"],
        task["Devices"]["link_metrics"]["server_address"],
        task["frequency"],
        task["Devices"]["link_metrics"]["bandwidth"],
        task["Devices"]["link_metrics"]["jitter"],
        task["Devices"]["link_metrics"]["packet_loss"],
        latency_config
    )

    # Parse alert flow conditions
    alertflow = task["Devices"]["AlertFlowConditions"]["alertflow"]
    if alertflow:
        alertflow_conditions = AlertflowConditions(
            True,
            task["Devices"]["AlertFlowConditions"]["cpu_usage"],
            task["Devices"]["AlertFlowConditions"]["ram_usage"],
            task["Devices"]["AlertFlowConditions"]["interface_stats"],
            task["Devices"]["AlertFlowConditions"]["packet_loss"],
            task["Devices"]["AlertFlowConditions"]["jitter"]
        )
    else:
        alertflow_conditions = AlertflowConditions()

    # Create the config object combining all the parsed metrics and conditions
    config = Config(device_metrics, link_metrics, alertflow_conditions)

    # Create the task object and return it
    task_obj = Task(lastTask, task["type"], task["frequency"], task["duration"], task["devices"], config)
    return task_obj
