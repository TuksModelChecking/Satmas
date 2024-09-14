import { create } from "zustand";
import { Parameters } from "../mra/parameters";
import { proto, experiment } from "../../wailsjs/wailsjs/go/models";

export type ExperimentStateType = {
    parameters: Parameters
    agents: Map<string, proto.Agent>
    resources: Set<string>
    message: string,
    loaded: boolean,

    setMessage: (newMessage: string) => void;
    setParameters: (newParameters: Parameters) => void;
    addAgent: (agent: proto.Agent) => void;
    setAgentDemand: (agentID: string, demand: number) => void;
    removeAgent: (agentID: string) => void;
    addResource: (resource: string) => void;
    removeResource: (resource: string) => void;
    addResourceAccess: (agentID: string, resource: string) => void;
    setExperiment: (experiment: experiment.TSExperiment) => void;
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
    loaded: false,

    setMessage: (newMessage: string) => set(() => ({ message: newMessage })),
    setParameters: (newParameters: Parameters) => set(() => ({ parameters: newParameters })),
    addAgent: (agent: proto.Agent) => {
        console.log(agent);
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
    setExperiment: (experiment) => {
        set((state) => {
            state.parameters = {
                algorithm: Number(experiment.algorithm) as proto.SynthesisAlgorithm,
                numberOfIterations: Number(experiment.numberOfIterations),
                timebound: Number(experiment.timebound),
            };

            const agents = new Map<string, proto.Agent>();
            let index = 1;
            for (let agt of (experiment.mra?.agents ?? new Array<proto.Agent>)) {
                agt.id = String(index++);
                agents.set(agt.id ?? "", agt);
            }

            state.agents = agents;
            state.resources = new Set<string>(experiment.mra?.resources);

            state.loaded = !state.loaded;

            return {
                ...state,
            };
        })
    },
}));

export default useExperimentState;