"""
    Problem.py - Definitions related to the Multi-Agent for resource allocation problem
"""

from dataclasses import dataclass
from typing import List, Dict
from yaml import SafeLoader
from yaml import load

from Problem.agent import Agent

@dataclass
class MRA:
    agt: List[Agent] 
    res: List[int]
    coalition: List[int]

    # Agt^+ = Agt + a_0
    def num_agents_plus(self):
        return len(self.agt) + 1

    def num_resources(self):
        return len(self.res)

@dataclass
class Problem:
    mra: MRA
    k: int

"""
    Reads in a MRA scenario from a file

    Parameters:
    - ymal_path: Path to configuration yml file as string

    Returns:
    Returns MRA instance
"""
def read_in_mra(ymal_path: str):
    yml_data: Dict = load(open(ymal_path, "r"), Loader=SafeLoader)
    agents = []
    resources: set = set()
    for a_name in yml_data["agents"]:
        agent = Agent(
            id=int(a_name[1:]),
            acc=list(map(lambda r: int(r[1:]), yml_data[a_name]["access"])),
            d=yml_data[a_name]["demand"]
        )
        for resource in agent.acc:
            resources.add(resource)
        agents.append(agent)

    return Problem(
        mra=MRA(
            agt=agents,
            res=list(resources),
            coalition=list(map(lambda a: int(a[1:]), yml_data["coalition"]))
        ),
        k=int(yml_data["k"])
    )

