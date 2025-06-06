import re
from collections import defaultdict
from math import ceil, log
from mra.problem import MRA


class TimeStep:
    """
    Analyzes and represents the state of the MRA system at a specific time step.
    """
    def __init__(self, t: int, named_model: dict[str, bool], mra_problem: MRA):
        self.t = t
        self.named_model = named_model
        self.mra_problem = mra_problem 

        self.num_agents_plus = self.mra_problem.num_agents_plus()
        self.num_total_resources = self.mra_problem.num_resources()

        # Bits for agent ID encoding (for resource allocation)
        self.m_agent_id_bits = ceil(log(self.num_agents_plus, 2)) if self.num_agents_plus > 1 else 0
        
        # Bits for action encoding
        self.num_possible_actions = (self.num_total_resources * 2) + 2 # idle, relall, req_i, rel_i
        self.m_action_bits = 0
        if self.num_possible_actions > 0:
             self.m_action_bits = ceil(log(self.num_possible_actions, 2)) if self.num_possible_actions > 1 else 0

        self.resource_states: dict[int, int] = {} # 0-idx r_id -> 0-idx agent_id (a0, a1, ...)
        self.demand_fulfillment: dict[int, tuple[int, int]] = {} # 1-idx agent_id (a1,...) -> (held, total)
        self.agent_actions: dict[int, str] = {} # 1-idx agent_id (a1,...) -> action_string
        self.satisfied_agents: set[int] = set()  # Set of 1-idx agent IDs that have satisfied their demand

        self._parse_resource_states()
        self._calculate_demand_fulfillment()
        self._parse_actions()

    def _parse_resource_states(self):
        # Pattern: t{self.t}r<R>b<B> (R is 1-indexed resource ID)
        pattern = re.compile(rf"^t{self.t}r(\d+)b(\d+)$")
        temp_resource_bits = defaultdict(dict) # res_id_0_indexed -> {bit_idx: value}

        for var_name, truth_value in self.named_model.items():
            match = pattern.match(var_name)
            if match:
                res_id_1_indexed = int(match.group(1))
                bit_idx = int(match.group(2)) # 0-indexed bit (LSB)
                res_id_0_indexed = res_id_1_indexed - 1

                if 0 <= res_id_0_indexed < self.num_total_resources and \
                   0 <= bit_idx < self.m_agent_id_bits:
                    temp_resource_bits[res_id_0_indexed][bit_idx] = truth_value
        
        for r_idx_0 in range(self.num_total_resources):
            bits_map = temp_resource_bits.get(r_idx_0, {})
            agent_id_0_indexed = 0
            if self.m_agent_id_bits == 0: # Only agent a0 possible
                agent_id_0_indexed = 0
            else:
                for i in range(self.m_agent_id_bits): # i is bit_idx (0 for LSB)
                    if bits_map.get(i, False):
                        agent_id_0_indexed += (1 << i)
            self.resource_states[r_idx_0] = agent_id_0_indexed

    def _calculate_demand_fulfillment(self):
        # Counts resources held by each agent (0-indexed agent ID for a0, a1, ...)
        agent_0_indexed_held_counts = defaultdict(int)
        for holder_agent_id_0_indexed in self.resource_states.values():
            agent_0_indexed_held_counts[holder_agent_id_0_indexed] += 1

        # mra_problem.agt is a list of Agent objects (a_1, a_2, ...)
        for agent_obj in self.mra_problem.agt: # agent_obj.id is 1-indexed
            agent_id_1_indexed = agent_obj.id 
            total_demand = agent_obj.d
            # agent_id_1_indexed is the key for agent_0_indexed_held_counts
            # as a_1 has 0-indexed ID 1, a_2 has ID 2, etc.
            held_count = agent_0_indexed_held_counts.get(agent_id_1_indexed, 0)
            self.demand_fulfillment[agent_id_1_indexed] = (held_count, total_demand)
            
            # Check if agent has satisfied its demand
            if total_demand > 0 and held_count >= total_demand:
                self.satisfied_agents.add(agent_id_1_indexed)
            
    def _action_number_to_string(self, number: int) -> str:
        if number == 0: return "idle"
        if number == 1: return "relall"
        
        # For reqX, action_number = X*2. For relX, action_number = X*2+1
        # X is the 1-indexed resource ID.
        if number % 2 == 0: # Even, potentially req
            x = number // 2
            # Validate X against num_total_resources if strict interpretation is needed
            if x >= 1: # and x <= self.num_total_resources:
                return f"req{x}"
        else: # Odd, potentially rel
            x = (number - 1) // 2
            if x >= 1: # and x <= self.num_total_resources:
                return f"rel{x}"
        return f"unknown_action({number})" # Fallback

    def _parse_actions(self):
        # Pattern: t{self.t}act_a<A>b<B> (A is 1-indexed agent ID)
        pattern = re.compile(rf"^t{self.t}act_a(\d+)b(\d+)$")
        temp_action_bits = defaultdict(dict) # agent_id_1_indexed -> {bit_idx: value}

        for var_name, truth_value in self.named_model.items():
            match = pattern.match(var_name)
            if match:
                agent_id_1_indexed = int(match.group(1))
                bit_idx = int(match.group(2)) # 0-indexed bit (LSB)

                # Check if this agent_id_1_indexed is one of the actual agents
                is_valid_agent = any(ag.id == agent_id_1_indexed for ag in self.mra_problem.agt)
                
                if is_valid_agent and 0 <= bit_idx < self.m_action_bits:
                    temp_action_bits[agent_id_1_indexed][bit_idx] = truth_value
        
        for agent_obj in self.mra_problem.agt: # Iterate through actual agents
            agent_id_1_idx = agent_obj.id
            bits_map = temp_action_bits.get(agent_id_1_idx, {})
            
            action_num = 0
            if self.m_action_bits == 0: # Only one action possible (e.g. "idle" if num_possible_actions is 1)
                # Assuming action_num 0 is the default if no bits.
                action_num = 0 
            else:
                for i in range(self.m_action_bits): # i is bit_idx (0 for LSB)
                    if bits_map.get(i, False):
                        action_num += (1 << i)
            
            self.agent_actions[agent_id_1_idx] = self._action_number_to_string(action_num)

    def get_formatted_string(self) -> str:
        lines = []

        # 1. Format resource states: [r1=0, r2=0, r3=0]_t
        state_parts = []
        if self.num_total_resources == 0:
            state_parts.append("no_resources")
        else:
            # Sort by resource index for consistent output if not already guaranteed by range
            for r_idx_0 in range(self.num_total_resources):
                agent_id_0 = self.resource_states.get(r_idx_0, 0) # Default to a0
                state_parts.append(f"r{r_idx_0+1}={agent_id_0}") # Display r_idx+1 for 1-indexed
        lines.append(f"[{', '.join(state_parts)}]_{self.t}")

        # 2. Format demand fulfillment: [a1=H/D *a1, a2=H/D]
        demand_parts = []
        sorted_agent_ids_for_demand = sorted(self.demand_fulfillment.keys())

        if not sorted_agent_ids_for_demand and self.mra_problem.agt: # Agents exist, but no fulfillment data
             for agent_obj in self.mra_problem.agt: # Show all agents from problem
                 demand_parts.append(f"a{agent_obj.id}=0/{agent_obj.d}")
        elif not self.mra_problem.agt: # No agents in the problem
            pass # Or: demand_parts.append("no_agents_defined")
        else:
            for agent_id_1 in sorted_agent_ids_for_demand:
                held, total = self.demand_fulfillment[agent_id_1]
                demand_str = f"a{agent_id_1}={held}/{total}"
                if total > 0 and held >= total : # Mark if demand met (and demand is not 0)
                    demand_str += f" *"
                demand_parts.append(demand_str)
        
        if demand_parts: # Only add line if there's demand info to show
            lines.append(f"[{', '.join(demand_parts)}]")

        # 3. Format actions: [a1_req1, a2_rel2]
        action_parts = []
        sorted_agent_ids_for_actions = sorted(self.agent_actions.keys())

        if not sorted_agent_ids_for_actions and self.mra_problem.agt:
            # If no actions parsed but agents exist, could show default or placeholder
            # for agent_obj in self.mra_problem.agt: action_parts.append(f"a{agent_obj.id}_no_action")
            pass # For now, omit line if no actions explicitly found
        else:
            for agent_id_1 in sorted_agent_ids_for_actions:
                action_str = self.agent_actions[agent_id_1]
                action_parts.append(f"a{agent_id_1}_{action_str}")
        
        if action_parts: # Only add line if there are actions to show
            lines.append(f"[{', '.join(action_parts)}]")

        return "\n".join(lines)


class ModelInterpreter:
    """
    Interprets a raw SAT model output to generate a step-by-step trace
    of resource allocations, agent demand fulfillment, and actions.
    """
    def __init__(self, raw_model: list[int], vpool, mra_problem):
        """
        Initializes the ModelInterpreter.

        Args:
            raw_model: The raw model (list of integers) from the SAT solver.
            vpool: The PySAT VarPool object used for encoding.
            mra_problem: The MRAProblem object containing agent definitions, resource counts, etc.
        """
        self.raw_model = raw_model if raw_model else []
        self.vpool = vpool
        self.mra_problem = mra_problem
        self.named_model: dict[str, bool] = self._to_named_model()
        self.max_time_step = self._find_max_time_step()
        self.loop_size = self._find_loop_size()
        self.time_steps = []
        self._process_time_steps()

    def _to_named_model(self) -> dict[str, bool]:
        if not self.raw_model:
            return {}
        model = {}
        for var_int in self.raw_model:
            obj = self.vpool.obj(abs(var_int))
            if obj is not None:
                 model[obj] = var_int > 0
        return model

    def _find_max_time_step(self) -> int:
        max_t = -1
        if not self.named_model:
            return max_t
        
        # General time pattern to find max_time_step from any t-variable
        time_var_pattern = re.compile(r"^t(\d+)")
        for var_name in self.named_model.keys():
            match = time_var_pattern.match(var_name)
            if match:
                t = int(match.group(1))
                if t > max_t:
                    max_t = t
        return max_t
    
    def _find_loop_size(self) -> int:
        """Find loop size from the model using loopSize_{k} variables"""
        loop_size_pattern = re.compile(r"^loopSize_(\d+)$")
        
        for var_name, truth_value in self.named_model.items():
            match = loop_size_pattern.match(var_name)
            if match and truth_value:
                return int(match.group(1))
        return 0  # Default if not found
    
    def _process_time_steps(self):
        """Process all time steps and store them for analysis"""
        for t_idx in range(self.max_time_step + 1):
            self.time_steps.append(TimeStep(t_idx, self.named_model, self.mra_problem))
    
    def calculate_payoff(self) -> float:
        """
        Calculate the payoff based on goal satisfaction divided by loop size.
        Returns the payoff as a float value.
        """
        if self.loop_size <= 0:
            return 0.0
        
        # Count how many times agents reach their goal across all time steps
        goal_count = 0
        for time_step in self.time_steps:
            goal_count += len(time_step.satisfied_agents)
        
        return goal_count / self.loop_size if self.loop_size > 0 else 0.0

    def get_goal_satisfaction_summary(self) -> dict:
        """
        Get a summary of goal satisfaction per agent and time step.
        Returns a dictionary mapping agent IDs to lists of time steps where they reach their goal.
        """
        summary = defaultdict(list)
        for t, time_step in enumerate(self.time_steps):
            for agent_id in time_step.satisfied_agents:
                summary[agent_id].append(t)
        return dict(summary)

    def format_complete_trace(self) -> str:
        """
        Formats the entire trace of the system over all time steps with improved readability.
        """
        if self.max_time_step == -1 and not self.named_model:  # Handle empty/UNSAT model
            if self.mra_problem.num_resources() > 0:  # If there are resources, show initial state
                # Create a TimeStep for t=0 even if no model vars exist for t=0
                ts_obj_initial = TimeStep(0, {}, self.mra_problem)
                return ts_obj_initial.get_formatted_string()
            else:
                return "No time steps found in model and no resources to display for t=0."

        # Calculate payoff for the entire loop
        payoff = self.calculate_payoff()
        summary = self.get_goal_satisfaction_summary()
        
        # Create a header section with important overview information
        header = [
            "╔══════════════════════════════════════════",
            f"║ Loop Size: {self.loop_size:<30} ",
            f"║ Payoff: {payoff:.4f} ({sum(len(t) for t in summary.values())} goal states/{self.loop_size} steps)",
            "╚══════════════════════════════════════════"
        ]
        
        # Add agent satisfaction summary
        summary_lines = ["", "━━━ Agent Goal Satisfaction Summary ━━━"]
        for agent_id in sorted(summary.keys()):
            times = summary[agent_id]
            agent_obj = next((a for a in self.mra_problem.agt if a.id == agent_id), None)
            demand = agent_obj.d if agent_obj else "?"
            
            summary_lines.append(f"Agent {agent_id} (demand={demand}): Goal reached {len(times)} times")
            if times:
                time_groups = self._group_consecutive_numbers(times)
                time_str = ", ".join([
                    f"t={g[0]}" if len(g) == 1 else f"t={g[0]}-{g[-1]}" 
                    for g in time_groups
                ])
                summary_lines.append(f"  At time steps: {time_str}")
        
        # Build the trace visualization
        trace_parts = []
        for t_idx in range(self.max_time_step + 1):
            # Add time step header to visually separate steps
            if t_idx > 0:
                trace_parts.append("")
                trace_parts.append(f"┈┈┈ Time Step {t_idx} ┈┈┈")
            else:
                trace_parts.append(f"┈┈┈ Time Step {t_idx} (Initial) ┈┈┈")
            
            # Add the formatted time step content
            ts_obj = self.time_steps[t_idx]
            trace_parts.append(ts_obj.get_formatted_string())
            
        # Combine everything
        result = "\n".join(header + summary_lines + ["", "━━━ Complete Execution Trace ━━━"] + trace_parts)
        return result
    
    def _group_consecutive_numbers(self, numbers):
        """Helper method to group consecutive numbers for prettier display"""
        if not numbers:
            return []
        
        result = []
        current_group = [numbers[0]]
        
        for i in range(1, len(numbers)):
            if numbers[i] == numbers[i-1] + 1:
                current_group.append(numbers[i])
            else:
                result.append(current_group)
                current_group = [numbers[i]]
                
        result.append(current_group)
        return result
