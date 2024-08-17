import { create } from "zustand";
import { AlgorithmType, ExperimentExecutionState, Parameters, createParameters } from "./parameters";
import { createMRAState } from "./mra";
import { Agent } from "./agent";

export type ExperimentStateType = {
    parameters: Parameters
    agents: Map<string, Agent>
    resources: Set<string>
    message: string;

    setParameters: (newParameters: Parameters) => void;
    addAgent: (agent: Agent) => void;
    removeAgent: (agentID: string) => void;
    addResource: (resource: string) => void;
    removeResource: (resource: string) => void;
    addResourceAccess: (agentID: string, resource: string) => void;
};

// Global experiment state
const useExperimentState = create<ExperimentStateType>((set) => ({
    parameters: {
        algorithm: AlgorithmType.COLLECTIVE,
        numberOfIterations: 10,
        timebound: 5,
    } as Parameters,
    agents: new Map<string, Agent>(),
    resources: new Set<string>(),
    message: "",

    setParameters: (newParameters: Parameters) => set(() => ({ parameters: newParameters })),
    addAgent: (agent: Agent) => {
        set((state) => ({ agents: new Map<string, Agent>(state.agents).set(agent.getID(), agent) }))
    },
    removeAgent: (agentID: string) => {
        set((state) => {
            state.agents.delete(agentID);
            return { agents: new Map<string, Agent>(state.agents) };
        })
    },
    addResource: (resource: string) => {
        set((state) => ({ resources: new Set<string>(state.resources).add(resource) }))
    },
    removeResource: (resource: string) => {
        set((state) => {
            state.resources.delete(resource);
            return { resources: new Set<string>(state.resources) };
        })
    },
    addResourceAccess: (agentID: string, resource: string) => {
        set((state) => {
            const agent = state.agents.get(agentID);
            if (!agent) {
                return state;
            }
            agent.addResouceAccess(resource);
            return {
                agents: new Map<string, Agent>(state.agents),
            };
        })
    },
}));

export default useExperimentState;