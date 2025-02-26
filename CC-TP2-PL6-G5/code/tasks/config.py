from dataclasses import dataclass
from typing import List, Dict
import json

class Device_metrics:
    """
    Represents the device metrics such as CPU usage, RAM usage, and network interface statistics.
    """
    cpu_usage: bool
    ram_usage: bool
    interface_stats: List[str] 

    def __init__(self, cpu_usage: bool, ram_usage: bool, interface_stats: List[str]):
        """
        Initializes the Device_metrics object with the provided values.
        
        Args:
            `cpu_usage` (bool): A flag indicating whether to monitor CPU usage.
            `ram_usage` (bool): A flag indicating whether to monitor RAM usage.
            `interface_stats` (List[str]): A list of network interfaces to monitor, represented by their names.
        """
        self.cpu_usage = cpu_usage
        self.ram_usage = ram_usage
        self.interface_stats = interface_stats

    def to_dict(self):
        """
        Converts the `Device_metrics` object to a dictionary format for easier serialization.

        Returns:
            `dict`: A dictionary representation of the Device_metrics object.
        """
        return {
            "cpu_usage": self.cpu_usage,
            "ram_usage": self.ram_usage,
            "interface_stats": self.interface_stats
        }


class AlertflowConditions:
    """
    Defines the alert conditions based on system and network metrics, including CPU usage, RAM usage,
    interface statistics, packet loss, and jitter.
    """
    alertflow_conditions: bool
    cpu_usage: int   # % of CPU usage for alert
    ram_usage: int   # % of RAM usage for alert
    interface_stats: int  # Packets per second threshold for alert
    packet_loss: int  # % packet loss threshold for alert
    jitter_limit: int  # Jitter limit (in ms) for alert

    def __init__(self, alertflow_conditions=None, cpu_usage=None, ram_usage=None, interface_stats=None, packet_loss=None, jitter_limit=None):
        """
        Initializes the AlertflowConditions object with the provided values or defaults.
        
        Args:
            `alertflow_conditions` (bool, optional): Whether alert conditions are enabled. Defaults to False.
            `cpu_usage` (int, optional): CPU usage threshold for alert. Defaults to 0.
            `ram_usage` (int, optional): RAM usage threshold for alert. Defaults to 0.
            `interface_stats` (int, optional): Interface stats threshold (pps) for alert. Defaults to 0.
            `packet_loss` (int, optional): Packet loss threshold for alert. Defaults to 0.
            `jitter_limit` (int, optional): Jitter limit for alert in milliseconds. Defaults to 0.
        """
        self.alertflow_conditions = alertflow_conditions if alertflow_conditions is not None else False
        self.cpu_usage = cpu_usage if cpu_usage is not None else 0
        self.ram_usage = ram_usage if ram_usage is not None else 0
        self.interface_stats = interface_stats if interface_stats is not None else 0
        self.packet_loss = packet_loss if packet_loss is not None else 0
        self.jitter_limit = jitter_limit if jitter_limit is not None else 0        

    def to_dict(self):
        """
        Converts the AlertflowConditions object to a dictionary format for easier serialization.

        Returns:
            `dict`: A dictionary representation of the Alertflow Conditions object.
        """
        return {
            "alertflow": self.alertflow_conditions,
            "cpu_usage": self.cpu_usage,
            "ram_usage": self.ram_usage,
            "interface_stats": self.interface_stats,
            "packet_loss": self.packet_loss,
            "jitter": self.jitter_limit
        }


class LatencyConfig:
    """
    Defines the configuration for latency measurement, including whether latency should be measured 
    and the number of packets to send.
    """
    latency: bool
    destination: str
    packet_count: int

    def __init__(self, latency=None, packet_count=None):
        """
        Initializes the LatencyConfig object with the provided values or defaults.
        
        Args:
            `latency` (bool, optional): Whether to measure latency. Defaults to False.
            `packet_count` (int, optional): Number of packets to send for latency measurement. Defaults to 0.
        """
        self.latency = latency if latency is not None else False
        self.packet_count = packet_count if packet_count is not None else 0

    def to_dict(self):
        """
        Converts the LatencyConfig object to a dictionary format for easier serialization.

        Returns:
            `dict`: A dictionary representation of the LatencyConfig object.
        """
        return {
            "latency": self.latency,
            "packet_count": self.packet_count
        }


class Link_metrics:
    """
    Represents the link metrics including performance testing options using iperf, monitoring of bandwidth, 
    jitter, packet loss, and latency configuration.
    """
    use_iperf: bool
    server: str
    duration: int
    server_address: str
    frequency: int
    bandwidth: bool
    jitter: bool
    packet_loss: bool
    latency: LatencyConfig

    def __init__(self, use_iperf: bool, server: str, duration: int, server_address: str, frequency: int, bandwidth: bool, jitter: bool, packet_loss: bool, latency: LatencyConfig):
        """
        Initializes the Link_metrics object with the provided values for performance testing and monitoring.
        
        Args:
            `use_iperf` (bool): Whether to use iperf for performance testing.
            `server` (str): The server used for iperf.
            `duration` (int): Duration of the iperf test (in seconds).
            `server_address` (str): The address of the iperf server.
            `frequency` (int): Frequency of tests.
            `bandwidth` (bool): Whether to monitor bandwidth.
            `jitter` (bool): Whether to monitor jitter.
            `packet_loss` (bool): Whether to monitor packet loss.
            `latency` (LatencyConfig): Latency configuration (packet count, whether to measure latency).
        """
        self.use_iperf = use_iperf
        self.server = server
        self.duration = duration
        self.server_address = server_address
        self.frequency = frequency
        self.bandwidth = bandwidth
        self.jitter = jitter
        self.packet_loss = packet_loss
        self.latency = latency

    def to_dict(self):
        """
        Converts the Link_metrics object to a dictionary format for easier serialization.

        Returns:
            `dict`: A dictionary representation of the Link_metrics object.
        """
        return {
            "use_iperf": self.use_iperf,
            "server": self.server,
            "duration": self.duration,
            "server_address": self.server_address,
            "frequency": self.frequency,
            "bandwidth": self.bandwidth,
            "jitter": self.jitter,
            "packet_loss": self.packet_loss,
            "latency": self.latency.latency,
            "packet_count": self.latency.packet_count
        }


class Config:
    """
    Represents the complete configuration including device metrics, link metrics, and AlertFlow conditions.
    This is used to manage all monitoring settings.
    """
    device_metrics: Device_metrics
    link_metrics: Link_metrics
    alertflow_conditions: AlertflowConditions

    def __init__(self, device_metrics: Device_metrics, link_metrics: Link_metrics, alertflow_conditions: AlertflowConditions):
        """
        Initializes the Config object with device metrics, link metrics, and AlertFlow conditions.
        
        Args:
            `device_metrics` (Device_metrics): The device monitoring configuration.
            `link_metrics` (Link_metrics): The link monitoring and testing configuration.
            `alertflow_conditions` (AlertflowConditions): The alert conditions configuration.
        """
        self.device_metrics = device_metrics
        self.link_metrics = link_metrics
        self.alertflow_conditions = alertflow_conditions

    def to_dict(self):
        """
        Converts the Config object to a dictionary format for easier serialization.

        Returns:
            `dict`: A dictionary representation of the Config object.
        """
        return {
            "devices_metric": self.device_metrics.to_dict(),
            "link_metrics": self.link_metrics.to_dict(),
            "AlertFlowConditions": self.alertflow_conditions.to_dict()
        }
