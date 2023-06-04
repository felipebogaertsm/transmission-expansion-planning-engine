from dataclasses import dataclass

import gurobipy as gb
import numpy as np


@dataclass
class PowerPlant:
    id: int
    capacity: float

    def __hash__(self):
        return hash(self.id)

    def get_restrictions(self, model: gb.Model) -> gb.Model:
        pass


@dataclass
class Load:
    value: float


@dataclass
class Node:
    id: int
    loads: list[Load]
    power_plants: list[PowerPlant]

    def __hash__(self):
        return hash(self.id)

    @property
    def total_generation_capacity(self) -> float:
        return np.sum([plant.capacity for plant in self.power_plants])

    @property
    def total_load(self) -> float:
        return np.sum([load.value for load in self.loads])


@dataclass
class TransmissionLine:
    id: str
    capacity: float
    reactance: float
    node_start: Node
    node_end: Node
    length: float
    cost_per_mile: float = 1e6
    is_real: bool = False

    def __hash__(self):
        return hash(self.id)

    @property
    def capital_cost(self) -> float:
        return self.cost_per_mile * self.length
