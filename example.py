from tepe.models import Load, Node, PowerPlant, TransmissionLine
from tepe.system import System

power_plant_1 = PowerPlant(_id=1, capacity=150e6)
power_plant_2 = PowerPlant(_id=2, capacity=360e6)
power_plant_3 = PowerPlant(_id=3, capacity=600e6)

load_1 = Load(value=80e6)
load_2 = Load(value=240e6)
load_3 = Load(value=40e6)
load_4 = Load(value=160e6)
load_5 = Load(value=240e6)

node_1 = Node(_id=1, loads=[load_1], power_plants=[power_plant_1])
node_2 = Node(_id=2, loads=[load_2], power_plants=[])
node_3 = Node(_id=3, loads=[load_3], power_plants=[power_plant_2])
node_4 = Node(_id=4, loads=[load_4], power_plants=[])
node_5 = Node(_id=5, loads=[load_5], power_plants=[])
node_6 = Node(_id=6, loads=[], power_plants=[power_plant_3])

transmission_lines = [
    TransmissionLine(
        _id="1-2",
        capacity=100e6,
        reactance=0.40,
        node_start=node_1,
        node_end=node_2,
        length=40,
        is_real=True,
    ),
    TransmissionLine(
        _id="1-3",
        capacity=100e6,
        reactance=0.38,
        node_start=node_1,
        node_end=node_3,
        length=38,
        is_real=False,
    ),
    TransmissionLine(
        _id="1-4",
        capacity=80e6,
        reactance=0.60,
        node_start=node_1,
        node_end=node_4,
        length=60,
        is_real=True,
    ),
    TransmissionLine(
        _id="1-5",
        capacity=100e6,
        reactance=0.20,
        node_start=node_1,
        node_end=node_5,
        length=20,
        is_real=True,
    ),
    TransmissionLine(
        _id="1-6",
        capacity=70e6,
        reactance=0.68,
        node_start=node_1,
        node_end=node_6,
        length=68,
        is_real=False,
    ),
    TransmissionLine(
        _id="2-3",
        capacity=100e6,
        reactance=0.20,
        node_start=node_2,
        node_end=node_3,
        length=20,
        is_real=True,
    ),
    TransmissionLine(
        _id="2-4",
        capacity=100e6,
        reactance=0.40,
        node_start=node_2,
        node_end=node_4,
        length=40,
        is_real=True,
    ),
    TransmissionLine(
        _id="2-5",
        capacity=100e6,
        reactance=0.31,
        node_start=node_2,
        node_end=node_5,
        length=31,
        is_real=False,
    ),
    TransmissionLine(
        _id="2-6",
        capacity=100e6,
        reactance=0.30,
        node_start=node_2,
        node_end=node_6,
        length=30,
        is_real=False,
    ),
    TransmissionLine(
        _id="3-4",
        capacity=82e6,
        reactance=0.59,
        node_start=node_3,
        node_end=node_4,
        length=59,
        is_real=False,
    ),
    TransmissionLine(
        _id="3-5",
        capacity=100e6,
        reactance=0.20,
        node_start=node_3,
        node_end=node_5,
        length=20,
        is_real=True,
    ),
    TransmissionLine(
        _id="3-6",
        capacity=100e6,
        reactance=0.48,
        node_start=node_3,
        node_end=node_6,
        length=48,
        is_real=False,
    ),
    TransmissionLine(
        _id="4-5",
        capacity=75e6,
        reactance=0.63,
        node_start=node_4,
        node_end=node_5,
        length=63,
        is_real=False,
    ),
    TransmissionLine(
        _id="4-6",
        capacity=100e6,
        reactance=0.30,
        node_start=node_4,
        node_end=node_6,
        length=30,
        is_real=False,
    ),
    TransmissionLine(
        _id="5-6",
        capacity=78e6,
        reactance=0.61,
        node_start=node_5,
        node_end=node_6,
        length=61,
        is_real=False,
    ),
]

system = System(transmission_lines=transmission_lines, s_base=100e6)
system.optimize()

print(f"Cost of the expansion: {system.expansion_cost * 1e-6:.2f}M USD")

print("\nLines to be constructed:")
for i, line in enumerate(system.transmission_lines):
    if int(round(system.line_control[str(i)].X)):
        print(line._id)
