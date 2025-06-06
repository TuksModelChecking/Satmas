import yaml
from typing import Tuple, Dict, Set, List

from mra.problem import MRA
from mra.agent import Agent

def parse_mra_from_yaml(file_path: str) -> Tuple[MRA, int, int]:
    """
    Parses an MRA problem definition from a YAML file.

    Args:
        file_path: Path to the YAML file.

    Returns:
        A tuple containing the MRA object, the start of time horizon k (inclusive),
        and the end of time horizon k (inclusive).
    """
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)

    # Extract k values (either as a single value or as a range)
    k_start = k_end = None
    if 'k' in data:
        if isinstance(data['k'], int):
            # If k is a single integer, use it for both start and end
            k_start = k_end = data['k']
        elif isinstance(data['k'], dict) and 'start' in data['k'] and 'end' in data['k']:
            k_start = data['k']['start']
            k_end = data['k']['end']
        else:
            raise ValueError("Invalid 'k' format. Expected integer or dict with 'start' and 'end' keys")
    else:
        raise ValueError("Missing required 'k' field in YAML file")
    
    # Process resources: map resource names (e.g., "r1") to integer IDs (e.g., 1)
    resource_name_to_id: Dict[str, int] = {}
    resource_set: Set[int] = set()
    if 'resources' in data:
        for i, r_name in enumerate(data['resources'], 1):
            resource_name_to_id[r_name] = i
            resource_set.add(i)

    # Process agents
    agents_list: List[Agent] = []
    agent_name_to_id: Dict[str, int] = {} # To map names like "a1" to integer IDs

    if 'agents' in data and isinstance(data['agents'], list):
        for i, agent_data in enumerate(data['agents'], 1):
            agent_id_name = agent_data['id'] # e.g., "a1"
            
            numerical_agent_id = agent_name_to_id.get(agent_id_name)
            if numerical_agent_id is None:
                numerical_agent_id = len(agent_name_to_id) + 1
                agent_name_to_id[agent_id_name] = numerical_agent_id

            demand = agent_data['demand']
            
            access_resource_ids: Set[int] = set()
            if 'access' in agent_data:
                for r_name_access in agent_data['access']:
                    if r_name_access in resource_name_to_id:
                        access_resource_ids.add(resource_name_to_id[r_name_access])
                    else:
                        raise ValueError(f"Agent {agent_id_name} accesses undefined resource '{r_name_access}'")
            
            agents_list.append(Agent(id=numerical_agent_id, d=demand, acc=access_resource_ids))
    
    mra_problem = MRA(agt=agents_list, res=resource_set)
    
    return mra_problem, k_start, k_end