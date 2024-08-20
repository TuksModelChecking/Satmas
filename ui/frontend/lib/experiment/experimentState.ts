import { create } from "zustand";
import { Parameters } from "../mra/parameters";
import { proto } from "../../wailsjs/wailsjs/go/models";

export type ExperimentStateType = {
    parameters: Parameters
    agents: Map<string, proto.Agent>
    resources: Set<string>
    message: string;

    setParameters: (newParameters: Parameters) => void;
    addAgent: (agent: proto.Agent) => void;
    setAgentDemand: (agentID: string, demand: number) => void;
    removeAgent: (agentID: string) => void;
    addResource: (resource: string) => void;
    removeResource: (resource: string) => void;
    addResourceAccess: (agentID: string, resource: string) => void;
};

// Global experiment state
const useExperimentState = create<ExperimentStateType>((set) => ({
    parameters: {
        algorithm: proto.SynthesisAlgorithm.COLLECTIVE,
        numberOfIterations: 10,
        timebound: 5,
    } as Parameters,
    agents: new Map<string, proto.Agent>(),
    resources: new Set<string>(),
    message: "",

    setParameters: (newParameters: Parameters) => set(() => ({ parameters: newParameters })),
    addAgent: (agent: proto.Agent) => {
        set((state) => ({ agents: new Map<string, proto.Agent>(state.agents).set(agent.id ?? "", agent) }))
    },
    setAgentDemand: (agentID: string, demand: number) => {
        set((state) => {
            const agent = state.agents.get(agentID);
            if (agent) {
                agent.demand = demand;
                state.agents.set(agentID, agent);
                return { agents: new Map<string, proto.Agent>(state.agents) };
            }
            return { agents: new Map<string, proto.Agent>(state.agents) };
        })
    },
    removeAgent: (agentID: string) => {
        set((state) => {
            state.agents.delete(agentID);
            return { agents: new Map<string, proto.Agent>(state.agents) };
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
            if (!agent.acc) {
                agent.acc = [];
            }
            agent.acc.push(resource);
            return {
                agents: new Map<string, proto.Agent>(state.agents),
            };
        })
    },
}));

export default useExperimentState;