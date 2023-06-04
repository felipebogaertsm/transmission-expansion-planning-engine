import gurobipy as gb
import numpy as np

from tepe.models import Node, PowerPlant, TransmissionLine


class System:
    """
    Represents a power system.

    :param list[TransmissionLine] transmission_lines: The list of transmission lines in the system.
    :param float s_base: The base apparent power in MVA.
    """

    def __init__(
        self, transmission_lines: list[TransmissionLine], s_base: float
    ) -> None:
        self.transmission_lines = transmission_lines
        self.s_base = s_base  # base apparent power in MVA

        self.model = gb.Model()

        self.expansion_cost = None

    @property
    def nodes(self) -> list[Node]:
        """
        Get the list of nodes in the system.

        :return: The list of nodes.
        :rtype: list[Node]
        """
        unique_nodes = set()

        for line in self.transmission_lines:
            unique_nodes.add(line.node_start)
            unique_nodes.add(line.node_end)

        return unique_nodes

    @property
    def power_plants(self) -> list[PowerPlant]:
        """
        Get the list of power plants in the system.

        :return: The list of power plants.
        :rtype: list[PowerPlant]
        """
        power_plants = []

        for node in self.nodes:
            for pp in node.power_plants:
                power_plants.append(pp)

        return power_plants

    @property
    def transmission_line_count(self) -> int:
        """
        Get the count of transmission lines in the system.

        :return: The count of transmission lines.
        :rtype: int
        """
        return len(self.transmission_lines)

    @property
    def node_count(self) -> int:
        """
        Get the count of nodes in the system.

        :return: The count of nodes.
        :rtype: int
        """
        return len(self.nodes)

    @property
    def power_plant_count(self) -> int:
        """
        Get the count of power plants in the system.

        :return: The count of power plants.
        :rtype: int
        """
        return len(self.power_plants)

    def get_susceptance_matrix(self) -> np.ndarray:
        """
        Get the susceptance matrix of the transmission lines.

        :return: The susceptance matrix.
        :rtype: np.ndarray
        """
        return np.array([1 / line.reactance for line in self.transmission_lines])

    def generate_variables(self) -> None:
        """
        Generate the optimization variables.
        """
        # Adding binary variables to indicate whether or not transmission lines should be built
        self.x = self.model.addVars(
            [str(i) for i, line in enumerate(self.transmission_lines)],
            vtype=gb.GRB.BINARY,
        )
        self.x_vars_map = {
            line: self.x[str(i)] for i, line in enumerate(self.transmission_lines)
        }

        # Adding variables for power plant generators
        self.generators = [self.model.addVar() for _ in range(self.power_plant_count)]
        self.generator_vars_map = {
            pp: generator for pp, generator in zip(self.power_plants, self.generators)
        }

        # Adding variables for the theta angles of each Node
        self.theta = [self.model.addVar() for _ in range(self.node_count)]
        self.theta_vars_map = {
            node: theta for node, theta in zip(self.nodes, self.theta)
        }

    def generate_power_plant_restrictions(self) -> None:
        """
        Generate the power plant restrictions.
        """
        for i, power_plant in enumerate(self.power_plants):
            capacity_pu = power_plant.capacity / self.s_base

            self.model.addConstr(self.generator_vars_map[power_plant] <= capacity_pu)
            self.model.addConstr(self.generator_vars_map[power_plant] >= 0)

    def generate_angle_restrictions(self) -> None:
        """
        Generate the angle restrictions.
        """
        for angle in self.theta:
            self.model.addConstr(angle <= np.pi)
            self.model.addConstr(angle >= -np.pi)

    def generate_line_restrictions(self) -> None:
        """
        Generate the line restrictions.
        """
        b = self.get_susceptance_matrix()

        for i, line in enumerate(self.transmission_lines):
            capacity_pu = line.capacity / self.s_base

            theta_1 = self.theta_vars_map[line.node_start]
            theta_2 = self.theta_vars_map[line.node_end]

            line_control_var = self.x_vars_map[line]

            # Candidate transmission lines:
            self.model.addConstr(
                -b[i] * (theta_1 - theta_2) * line_control_var <= capacity_pu
            )
            self.model.addConstr(
                -b[i] * (theta_2 - theta_1) * line_control_var <= capacity_pu
            )

            # Existing transmission lines:
            if line.is_real:
                self.model.addConstr(-b[i] * (theta_1 - theta_2) <= capacity_pu)
                self.model.addConstr(-b[i] * (theta_2 - theta_1) <= capacity_pu)

    def generate_node_restrictions(self) -> None:
        """
        Generate the node restrictions.
        """
        b = self.get_susceptance_matrix()

        for _, node in enumerate(self.nodes):
            generators = []
            loads_pu = node.total_load / self.s_base

            for power_plant in node.power_plants:
                generators.append(self.generator_vars_map[power_plant])

            line_terms = []

            for i, line in enumerate(self.transmission_lines):
                if line.node_start == node:
                    line_terms.append(
                        b[i]
                        * (
                            self.theta_vars_map[line.node_start]
                            - self.theta_vars_map[line.node_end]
                        )
                        * self.x_vars_map[line]
                    )
                    if line.is_real:
                        line_terms.append(
                            b[i]
                            * (
                                self.theta_vars_map[line.node_start]
                                - self.theta_vars_map[line.node_end]
                            )
                        )
                elif line.node_end == node:
                    line_terms.append(
                        b[i]
                        * (
                            self.theta_vars_map[line.node_end]
                            - self.theta_vars_map[line.node_start]
                        )
                        * self.x_vars_map[line]
                    )
                    if line.is_real:
                        line_terms.append(
                            b[i]
                            * (
                                self.theta_vars_map[line.node_end]
                                - self.theta_vars_map[line.node_start]
                            )
                        )

            self.model.addConstr(
                gb.quicksum(generators) - loads_pu - gb.quicksum(line_terms) == 0
            )

    def generate_restrictions(self) -> None:
        """
        Generate all the restrictions.
        """
        self.generate_power_plant_restrictions()
        self.generate_angle_restrictions()
        self.generate_line_restrictions()
        self.generate_node_restrictions()

    def optimize(self) -> None:
        """
        Optimize the power system.

        :return: The optimized model.
        :rtype: gb.Model
        """
        self.generate_variables()
        self.generate_restrictions()

        # Objective definition:
        fob = gb.quicksum(
            self.x[str(i)] * line.capital_cost
            for i, line in enumerate(self.transmission_lines)
        )
        self.model.setObjective(fob, sense=gb.GRB.MINIMIZE)
        self.model.optimize()

        self.expansion_cost = self.model.objVal
