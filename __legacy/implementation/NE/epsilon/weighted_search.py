from Problem.problem import Problem, MRA
from Problem.agent import Agent
from NE.shared import run_solver, run_solver_temp
from SATSolver.solver import iterative_solve_simple
from NE.utils import h_calculate_weight_update, h_choose_action_greedy, h_choose_action_idle, h_build_full_strategy, h_build_variable_agent_weight_map, h_count_relall, h_calculate_improvement

from SATSolver.logic_encoding import build_state_observation_from_string, state_observation_to_string
from SATSolver.logic_encoding import get_strategy_profile, encode_mra, encode_mra_with_strategy, encode_mra_simple, h_get_all_observed_resource_states, h_get_all_possible_actions_for_state_observation, state_observation_to_string

import networkx as nx

from dataclasses import dataclass
from typing import List, Set
import math
import copy
import time

@dataclass
class Node:
    agt_id: int
    demand: int
    denominator: int
    resources: Set[int]
    edges: List['Node']
    num_common: int
    visited: bool = False

    def __eq__(self, o):
        if isinstance(o, Node):
            # Compare the 'value' attribute of both instances
            return self.agt_id == o.agt_id
        return False

def build_contestion_graph(problem: Problem):
    # Build initial agent graph
    graph = {}
    for agt in problem.mra.agt:
        graph[agt.id] = Node(agt.id, agt.d, 0, set(agt.acc), [], 0)

    # Check for resource contestion relationships O(V^2) (Builds contestion graph)
    for node1_id in graph:
        for node2_id in graph:
            if node1_id != node2_id:
                node1 = graph[node1_id]
                node2 = graph[node2_id]

                # O(min(len(node1.resources), len(node2.resources)))
                if node1.resources.intersection(node2.resources):
                    node1.edges.append(node2_id)
                    node1.num_common += len(node1.resources.intersection(node2.resources))
                    node1.denominator += node2.demand

    # Determine connected components
    components = find_connected_components(graph)
    
    return graph, components

def build_weight_map_from_graph(graph, components, problem):
    weight_map = {}
    for component in components:
        lcm = 1
        if len(component) != 1:
            demand_ratios = []
            for node_id in component:
                node = graph[node_id]
                demand_ratios.append(node.denominator)

            lcm = math.lcm(*demand_ratios)
        else:
            graph[component[0]].denominator = 1

        for node_id in component:
            node = graph[node_id]
            scale_value = lcm / node.denominator
            weight_map[node.agt_id] = int(scale_value * node.demand * node.num_common)
    
    return weight_map

def solve(problem: Problem):

    # Build contestion graph
    graph, components = build_contestion_graph(problem)

    # Determine weight map
    weight_map = build_weight_map_from_graph(graph, components, problem)
    
    # Build sub problems
    sub_problems = build_sub_problems(problem, components)

    # Solve sub-problems
    final_sp = {}
    for sub_problem in sub_problems:
        for agt_id in sub_problem[2]:
            final_sp[sub_problem[2][agt_id]] = {}

    final_goal_map = {}
    fraction_map = {}

    for sub_problem in sub_problems:
        (sp, gm) = run_solver(sub_problem[0], goal_weight_map=weight_map)
        
        for agt_id in sub_problem[2]:
            for state_action_pair in sp[agt_id]:
                state_observation = build_state_observation_from_string(state_action_pair)
                action = sp[agt_id][state_action_pair]

                for state in state_observation:
                    # Rename agents
                    if state.a != 0:
                        state.a = sub_problem[2][state.a]

                    # Rename resources
                    state.r = sub_problem[1][state.r]

                actions = []
                for act in action:
                    if act[:3] == "req":
                        resource_id = int(act[5:])
                        actions.append(f"req_r{sub_problem[1][resource_id]}")
                    elif act[:3] == "rel" and act != "relall":
                        resource_id = int(act[5:])
                        actions.append(f"rel_r{sub_problem[1][resource_id]}")
                    else:
                        actions.append(act)

                final_sp[sub_problem[2][agt_id]][state_observation_to_string(state_observation)] = actions
                final_goal_map[sub_problem[2][agt_id]] = gm[agt_id]
        
        for agt_id in sub_problem[2]:
            (_, alternate_gm) = run_solver(sub_problem[0], agent_not_fix_id=agt_id, strategy_profile=sp)
            fraction_map[sub_problem[2][agt_id]] = alternate_gm[agt_id] / final_goal_map[sub_problem[2][agt_id]]

    return final_sp, weight_map, graph, final_goal_map, fraction_map

def find_connected_components(graph):
    def dfs(node, component):
        node.visited = True
        components[component].append(node.agt_id)
        for neighbor in node.edges:
            if not graph[neighbor].visited:
                dfs(graph[neighbor], component)

    num_vertices = len(graph)
    components = []

    for node in graph:
        if not graph[node].visited:
            components.append([])
            dfs(graph[node], len(components) - 1)

    return components

def _build_networkx_graph(graph):
    G = nx.Graph()

    # Add nodes
    for node_id in graph:
        G.add_node(node_id)

    # Add edges
    for node_id in graph:
        for edge_node in graph[node_id].edges:
            G.add_edge(node_id, edge_node)

    return G

def max_components(G, articulation_points):
    point_component_map = {}

    # Analyze impact of removing each articulation point
    for articulation_point in articulation_points:
        # Temporarily remove the articulation point from the graph
        temp_graph = G.copy()
        temp_graph.remove_node(articulation_point)
    
        # Find connected components sizes after removal
        connected_components_sizes = [len(comp) for comp in nx.connected_components(temp_graph)]
    
        point_component_map[articulation_point] = connected_components_sizes

    return point_component_map

def remove_node_from_graph(graph, del_node):
    node = None
    for node_id in graph:
        if node_id == del_node:
            node = graph[node_id]
            del graph[node_id]
            break

    for node_id in graph:
        for i in range(len(graph[node_id].edges)):
            if graph[node_id].edges[i] == del_node:
                del graph[node_id].edges[i]
                break
    
    return graph, node

def partition_graph(graph, max_depth, curr_depth = 0, partitions = [], articulation_points = [], additional_point = None):

    G = _build_networkx_graph(graph)

    flow_centrality = nx.current_flow_closeness_centrality(G)
    articulation_point = max(zip(flow_centrality.values(), flow_centrality.keys()))[1]

    articulation_points.append(articulation_point)
    # print(max_components(G, articulation_points))

    temp_G = G.copy()
    temp_G.remove_node(articulation_point)

    temp_graph = copy.deepcopy(graph)
    temp_graph, del_node = remove_node_from_graph(graph, articulation_point)

    connected_components = list(nx.connected_components(temp_G))

    # print(f"Points: {articulation_point} - Components: {connected_components}")

    for component in connected_components:
        sub_graph = {node_id:temp_graph[node_id] for node_id in component}
        temp = list(component)
        temp.append(articulation_point)
        
        if additional_point is not None:
            temp.append(additional_point)
            additional_point = None

        if curr_depth != max_depth and len(component) > 3:
            print(f"Points: {articulation_point} - Component: {component}")
            partition_graph(sub_graph, max_depth, curr_depth+1, partitions, articulation_points, articulation_point)
        else:
            partitions.append(temp)

        # temp.append(articulation_point)

def articulation_search(problem: Problem):
    # Build contestion graph
    graph, c = build_contestion_graph(problem)

    # Determine weight map
    weight_map = build_weight_map_from_graph(graph, c, problem)

    p = []
    a = []
    partition_graph(graph, 1, partitions=p, articulation_points=a)

    sub_problems = build_sub_problems(problem, p)
    
    final_sp = {}
    for sub_problem in sub_problems:
        for agt_id in sub_problem[2]:
            final_sp[sub_problem[2][agt_id]] = {}

    """
    fixed_sps = []
    counter = 0
    for sub_problem in sub_problems:
        temp_sp = {}
        key = list(sub_problem[2].keys())[-1]
        if key not in temp_sp:
            temp_sp[key] = {}

        agt = sub_problem[0].mra.agt[key-1]
        temp_sp[key] = h_build_full_strategy(
            agt,
            temp_sp[key], 
            h_get_all_observed_resource_states(agt, sub_problem[0].mra.agt),
            h_choose_action_greedy
        )

        fixed_sps.append(temp_sp)
        counter += 1
    """

    final_goal_map = {}
    fraction_map = {}
    counter = 0

    for sub_problem in sub_problems:
        (sp, gm) = run_solver(sub_problem[0], goal_weight_map=weight_map)

        for agt_id in sub_problem[2]:
            for state_action_pair in sp[agt_id]:
                state_observation = build_state_observation_from_string(state_action_pair)
                action = sp[agt_id][state_action_pair]

                for state in state_observation:
                    # Rename agents
                    if state.a != 0:
                        state.a = sub_problem[2][state.a]

                    # Rename resources
                    state.r = sub_problem[1][state.r]

                actions = []
                for act in action:
                    if act[:3] == "req":
                        resource_id = int(act[5:])
                        actions.append(f"req_r{sub_problem[1][resource_id]}")
                    elif act[:3] == "rel" and act != "relall":
                        resource_id = int(act[5:])
                        actions.append(f"rel_r{sub_problem[1][resource_id]}")
                    else:
                        actions.append(act)

                final_sp[sub_problem[2][agt_id]][state_observation_to_string(state_observation)] = actions
                final_goal_map[sub_problem[2][agt_id]] = gm[agt_id]

    for agt_id in final_sp:
        print(final_sp[agt_id])
        print()

    # (final_sp, g) = run_solver(problem, agent_not_fix_id=4, strategy_profile=final_sp)

    fraction_map = calculate_fraction_vector(problem, final_sp, final_goal_map, graph)
    print(fraction_map)

def calculate_fraction_vector(problem, final_sp, final_goal_map, graph):
    fraction_map = {}

    for agt in problem.mra.agt:
        (_, alternate_gm) = run_solver(problem, agent_not_fix_id=agt.id, strategy_profile=final_sp)

        if alternate_gm == False:
            for neighbour in graph[agt.id].edges:
                if neighbour in final_sp:
                    del final_sp[neighbour]
                    return calculate_fraction_vector(problem, final_sp, graph)

        if agt.id in final_goal_map:
            fraction_map[agt.id] = alternate_gm[agt.id] / final_goal_map[agt.id]
        else:
            fraction_map[agt.id] = alternate_gm[agt.id] / g[agt.id]

    return fraction_map

def build_sub_problems(problem: Problem, components):
    sub_problems = []
    for component in components:
        print(component)
        # Build sub-problem resources array
        resource_id_map = {}
        resource_id_reverse_map = {}
        r_id_counter = 1
        for r_id in problem.mra.res:
            first = True
            for agt_id in component:
                agt = problem.mra.agt[agt_id-1]
                if r_id in agt.acc:
                    resource_id_map[r_id_counter] = r_id
                    resource_id_reverse_map[r_id] = r_id_counter
                    if first == True:
                        r_id_counter += 1
                        first = False

        counter = 1
        for r_id in resource_id_reverse_map:
            resource_id_reverse_map[r_id] = counter
            counter += 1
        
        # Build problem agt array
        agt_id_map = {}
        id_map = {}
        id_counter = 1
        for agt_id in component:
            agt = problem.mra.agt[agt_id-1]
            agt_id_map[id_counter] = Agent(
                id=id_counter,
                acc=[resource_id_reverse_map[x] for x in agt.acc],
                d=agt.d
            )            
            id_map[id_counter] = int(agt_id)
            id_counter += 1

        sub_problems.append(
            [Problem(
                mra=MRA(
                    agt=list(agt_id_map.values()),
                    res=list(resource_id_map.keys()),
                    coalition=[1]
                ),
                k=problem.k
            ), resource_id_map, id_map]
        )

    return sub_problems

