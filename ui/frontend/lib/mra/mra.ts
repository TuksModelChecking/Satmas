import { Agent } from "./agent";

export const createMRAState = (set: any) => ({
    agents: Array<Agent>,
    resources: Array<string>,
    addAgent: (agent: Agent) => set((state: any) => (new Array<Agent>(...[...state.agents, agent]))),
    addResource: (resource: string) => set((state: any) => (new Array<string>(...[...state.resources, resource]))),
})
