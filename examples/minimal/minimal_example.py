import sys
import os
import yaml
from typing import Dict, List, Any

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from mra.problem import MRA
from mra.agent import Agent
from utils.yaml_parser import parse_mra_from_yaml
from solvers.pysat_solver import solve_mra_with_pysat
from core.pysat_constructs import vpool

from encoding.SBMF_2021.definition_17 import m as calculate_m_bits
resource_id_to_name_map = {}
agent_id_to_name_map = {}

def get_action_from_number(action_num: int, num_total_resources: int, resource_map: Dict[int, str]) -> str:
    """
    Reverses the logic of action_number from definition_20.py.
    Needs num_total_resources to determine if a number corresponds to req/rel.
    """
    if action_num == 0:
        return "Idle"
    elif action_num == 1:
        return "Release All"
    
    # Check req/rel actions
    # action_num = res_id * 2 for req
    # action_num = res_id * 2 + 1 for rel
    # Max resource_id related action_num would be num_total_resources * 2 + 1
    
    if action_num % 2 == 0: # Potential req
        res_id_candidate = action_num // 2
        if 1 <= res_id_candidate <= num_total_resources:
            res_name = resource_map.get(res_id_candidate, f"ResID_{res_id_candidate}")
            return f"Request {res_name}"
    else: # Potential rel
        res_id_candidate = (action_num - 1) // 2
        if 1 <= res_id_candidate <= num_total_resources:
            res_name = resource_map.get(res_id_candidate, f"ResID_{res_id_candidate}")
            return f"Release {res_name}"
            
    return f"UnknownActionNum_{action_num}"


def populate_id_to_name_maps_from_raw_yaml(raw_yaml_data: Dict[str, Any], parsed_mra: MRA):
    """
    Populates mapping from numerical IDs back to original names from YAML.
    This is crucial for readable output. It tries to match names to the IDs
    assigned by the parser.
    """

    # Resources: YAML parser assigns 1-based consecutive IDs.
    if 'resources' in raw_yaml_data:
        for i, r_name in enumerate(raw_yaml_data['resources'], 1):
            resource_id_to_name_map[i] = r_name

    for agent_obj in parsed_mra.agt:
        # Try to find a raw agent data that could correspond to this parsed agent_obj
        # This is a heuristic. A more robust way is if parser returns the name map.
        # For now, we assume agent_obj.id is the numerical ID we want to map.
        # And we try to find its original string name.
        # If agent_obj.id was directly an int in YAML, this is harder without more info.
        # If it was a string like "a1", the parser converted it.
        
        # Attempt to find the original name by iterating through raw_yaml_data['agents']
        # and matching properties or relying on the order if parser maintains it.
        # A simpler approach for this example: if agent.id is small, assume it's 1-based index.
        # This part is tricky without knowing exactly how `parse_mra_from_yaml` maps all cases.
        # Let's assume for "a1", "a2", etc., the parser creates IDs 1, 2, ...
        
        # Fallback: if we can't find a name, use "Agent<ID>"
        found_name = f"Agent{agent_obj.id}" # Default
        
        # Try to match based on the order and known parsing behavior for simple cases
        # (e.g. "a1" -> 1, "a2" -> 2)
        if 'agents' in raw_yaml_data:
            for i, raw_agent_spec in enumerate(raw_yaml_data['agents']):
                # This is a common pattern: "aN" maps to N or parser uses 1-based index
                if str(raw_agent_spec['id']).lower() == f"a{agent_obj.id}":
                    found_name = str(raw_agent_spec['id'])
                    break
                # If the parser uses 1-based indexing for agents in the list
                if (i + 1) == agent_obj.id and len(parsed_mra.agt) == len(raw_yaml_data['agents']):
                    found_name = str(raw_agent_spec['id'])
                    # only break if we are reasonably sure, otherwise keep looking or use default
                    # break 

        agent_id_to_name_map[agent_obj.id] = found_name


def get_resource_holder_name(res_id: int, t: int, mra_problem: MRA, solution_model: List[int]) -> str:
    """Decodes which agent holds the resource at time t, or if unassigned."""
    num_agents_for_encoding = mra_problem.num_agents_plus() # Total agents + 1 (for unassigned)
    num_bits = calculate_m_bits(num_agents_for_encoding)
    
    binary_value_str = []
    for i in range(num_bits):
        # Variable name format from encode_resource_state_at_t & binary_encode
        var_name = f"t{t}r{res_id}_b{i}"
        var_id = vpool.id(var_name) # Get ID from the central vpool

        if not var_id: # Should not happen if var was used in encoding
            return f"Error: Var '{var_name}' not in vpool"

        if var_id in solution_model:
            binary_value_str.append("1")
        elif -var_id in solution_model:
            binary_value_str.append("0")
        else:
            # This implies the variable's value was not determined or relevant to the solution.
            # For resource state bits, they should always be determined.
            return f"Bit {i} for r{res_id} (var: {var_name}, id: {var_id}) at t{t} undefined in model"

    if len(binary_value_str) != num_bits:
        return f"Incomplete binary data for r{res_id} at t{t}"

    try:
        # The binary string is MSB first (index 0 is MSB)
        assigned_numerical_id = int("".join(binary_value_str), 2)
    except ValueError:
        return f"Invalid binary string '{"".join(binary_value_str)}' for r{res_id} at t{t}"

    if assigned_numerical_id == 0:
        return "Unassigned"
    else:
        # Map numerical ID back to original agent name if possible
        return agent_id_to_name_map.get(assigned_numerical_id, f"AgentID_{assigned_numerical_id}")


def get_agent_action_details(agent: Agent, t: int, mra_problem: MRA, solution_model: List[int]) -> str:
    """Determines the action taken by an agent at time t by decoding action bits."""
    num_res = mra_problem.num_resources()
    num_possible_actions = (num_res * 2) + 2  # From definition_20.py logic
    num_action_bits = calculate_m_bits(num_possible_actions)

    action_bit_values = []
    action_var_prefix = f"t{t}act_a{agent.id}"

    for i in range(num_action_bits):
        bit_var_name = f"{action_var_prefix}_b{i}"
        bit_var_id = vpool.id(bit_var_name)

        if not bit_var_id:
            return f"Action bit '{bit_var_name}' missing in vpool"

        if bit_var_id in solution_model:
            action_bit_values.append("1")
        elif -bit_var_id in solution_model:
            action_bit_values.append("0")
        else:
            return f"Action bit {i} ('{bit_var_name}') for a{agent.id} at t{t} undefined in model"

    if len(action_bit_values) != num_action_bits:
        return f"Incomplete action bit data for a{agent.id} at t{t} (got {len(action_bit_values)}, expected {num_action_bits})"

    try:
        # action_bit_values is [LSB, ..., MSB]
        # int() expects the string to be "MSB...LSB"
        action_num = int("".join(reversed(action_bit_values)), 2)
    except ValueError:
        return f"Invalid binary string for action '{"".join(reversed(action_bit_values))}' for a{agent.id} at t{t}"

    return get_action_from_number(action_num, mra_problem.num_resources(), resource_id_to_name_map)


def get_agent_goal_status_str(agent: Agent, t: int, mra_problem: MRA, solution_model: List[int]) -> str:
    """Checks if an agent's goal is met at time t."""
    var_name = f"t{t}_g_a{agent.id}"
    var_id = vpool.id(var_name)

    if not var_id:
        return f"Goal variable '{var_name}' not in vpool"

    if var_id in solution_model:
        return "Met"
    elif -var_id in solution_model:
        return "Not Met"
    else:
        return f"Goal variable '{var_name}' (ID: {var_id}) undetermined in model"

def run_example():
    yaml_file_path = os.path.join(script_dir, "minimal_example.yml")

    print(f"--- SATMAS Minimal Example Runner ---")
    print(f"Loading MRA problem from: {yaml_file_path}\n")

    try:
        with open(yaml_file_path, 'r') as f:
            raw_yaml_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading YAML file: {e}")
        return

    try:
        mra_problem, k_val = parse_mra_from_yaml(yaml_file_path)
    except Exception as e:
        print(f"Error parsing YAML into MRA problem: {e}")
        return
        
    populate_id_to_name_maps_from_raw_yaml(raw_yaml_data, mra_problem)

    print("--- MRA Problem Definition ---")
    print(f"Time Horizon (k): {k_val}")
    
    res_details_list = []
    for r_id in sorted(list(mra_problem.res)):
        r_name = resource_id_to_name_map.get(r_id, f"ResID_{r_id}")
        res_details_list.append(f"{r_name} (ID: {r_id})")
    print(f"Resources: {{{', '.join(res_details_list) if res_details_list else 'None'}}}")
    
    print("Agents:")
    if not mra_problem.agt:
        print("  No agents defined.")
    for agent in mra_problem.agt:
        agent_name = agent_id_to_name_map.get(agent.id, f"AgentID_{agent.id}")
        acc_res_names = {resource_id_to_name_map.get(r_id, str(r_id)) for r_id in agent.acc}
        print(f"  - {agent_name} (ID: {agent.id}): Demand={agent.d}, Access={{{', '.join(sorted(list(acc_res_names))) if acc_res_names else 'None'}}}")

    try:
        solution_model = solve_mra_with_pysat(mra_problem, k_val)
    except Exception as e:
        print(f"Error during PySAT solving: {e}")
        import traceback
        traceback.print_exc()
        return

    if solution_model is not None:
        print("\n--- Solution Found! ---")
        
        named_model = {vpool.obj(abs(var)): var > 0 for var in solution_model}
        print("Named model:", named_model)

        print("\n--- Detailed Solution Trace (Times 0 to k) ---")
        for t in range(k_val + 1):
            print(f"\n[Time Step {t}]")
            
            print("  Resource States:")
            if not mra_problem.res:
                print("    No resources in problem.")
            for res_id in sorted(list(mra_problem.res)):
                res_name = resource_id_to_name_map.get(res_id, f"ResID_{res_id}")
                holder_info = get_resource_holder_name(res_id, t, mra_problem, solution_model)
                print(f"    {res_name}: Held by {holder_info}")

            print("  Agent Status:")
            if not mra_problem.agt:
                print("    No agents in problem.")
            for agent in mra_problem.agt:
                agent_name = agent_id_to_name_map.get(agent.id, f"AgentID_{agent.id}")
                action_info = get_agent_action_details(agent, t, mra_problem, solution_model)
                goal_info = get_agent_goal_status_str(agent, t, mra_problem, solution_model)
                print(f"    {agent_name}: Action -> {action_info} | Goal -> {goal_info}")
                
    else:
        print("\n--- No Solution Found ---")
        print("This means the problem as defined and encoded is unsatisfiable for the given k.")

if __name__ == "__main__":
    run_example()
