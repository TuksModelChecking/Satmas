export class Agent {
    private readonly id: string; // unique identifier of the agent
    private acc: Set<string>; // list of resource identifiers the agent has access to

    constructor(id: string, acc: string[]) {
        this.id = id;
        this.acc = new Set<string>(acc);
    }

    public addResouceAccess(resource: string) {
        this.acc.add(resource)
    }

    public getID(): string {
        return this.id;
    }

}