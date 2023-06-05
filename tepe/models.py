"""
tepe.models

This module defines the data classes for representing power plants, loads, 
nodes, and transmission lines.
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class PowerPlant:
    """
    Represents a power plant.

    :param int id: The ID of the power plant.
    :param float capacity: The capacity of the power plant.
    """

    _id: int
    capacity: float

    def __hash__(self):
        return hash(self._id)


@dataclass
class Load:
    """
    Represents a load.

    :param float value: The value of the load.
    """

    value: float


@dataclass
class Node:
    """
    Represents a node.

    :param int id: The ID of the node.
    :param list[Load] loads: The list of loads associated with the node.
    :param list[PowerPlant] power_plants: The list of power plants associated
        with the node.
    """

    _id: int
    loads: list[Load]
    power_plants: list[PowerPlant]

    def __hash__(self):
        return hash(self._id)

    @property
    def total_generation_capacity(self) -> float:
        """
        Calculate the total generation capacity of the node.

        :return: The total generation capacity.
        :rtype: float
        """
        return np.sum([plant.capacity for plant in self.power_plants])

    @property
    def total_load(self) -> float:
        """
        Calculate the total load of the node.

        :return: The total load.
        :rtype: float
        """
        return np.sum([load.value for load in self.loads])


@dataclass
class TransmissionLine:
    """
    Represents a transmission line.

    :param str id: The ID of the transmission line.
    :param float capacity: The capacity of the transmission line.
    :param float reactance: The reactance of the transmission line.
    :param Node node_start: The starting node of the transmission line.
    :param Node node_end: The ending node of the transmission line.
    :param float length: The length of the transmission line.
    :param float cost_per_mile: The cost per mile of the transmission line.
        Default is 1e6.
    :param bool is_real: Indicates if the transmission line exists or not.
        Default is False.
    """

    _id: str
    capacity: float
    reactance: float
    node_start: Node
    node_end: Node
    length: float
    cost_per_mile: float = 1e6
    is_real: bool = False

    def __hash__(self):
        return hash(self._id)

    @property
    def capital_cost(self) -> float:
        """
        Calculate the capital cost of the transmission line.

        :return: The capital cost.
        :rtype: float
        """
        return self.cost_per_mile * self.length
