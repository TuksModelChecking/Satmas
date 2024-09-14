export namespace experiment {
	
	export class Metadata {
	    // Go type: time
	    createdAt: any;
	    id: string;
	    numberOfAgents: number;
	    numberOfResources: number;
	    state: string;
	    pathToDefinition: string;
	    pathToResult: string;
	
	    static createFrom(source: any = {}) {
	        return new Metadata(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.createdAt = this.convertValues(source["createdAt"], null);
	        this.id = source["id"];
	        this.numberOfAgents = source["numberOfAgents"];
	        this.numberOfResources = source["numberOfResources"];
	        this.state = source["state"];
	        this.pathToDefinition = source["pathToDefinition"];
	        this.pathToResult = source["pathToResult"];
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	export class ReadOneExperimentRequest {
	    experimentID: string;
	
	    static createFrom(source: any = {}) {
	        return new ReadOneExperimentRequest(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.experimentID = source["experimentID"];
	    }
	}
	export class TSExperiment {
	    algorithm: string;
	    mra?: proto.MRA;
	    numberOfIterations: string;
	    timebound: string;
	    message: string;
	
	    static createFrom(source: any = {}) {
	        return new TSExperiment(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.algorithm = source["algorithm"];
	        this.mra = this.convertValues(source["mra"], proto.MRA);
	        this.numberOfIterations = source["numberOfIterations"];
	        this.timebound = source["timebound"];
	        this.message = source["message"];
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	export class ReadOneExperimentResponse {
	    experiment: TSExperiment;
	
	    static createFrom(source: any = {}) {
	        return new ReadOneExperimentResponse(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.experiment = this.convertValues(source["experiment"], TSExperiment);
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	export class TSActionList {
	    agentIDs: number[];
	    actions: string[];
	
	    static createFrom(source: any = {}) {
	        return new TSActionList(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.agentIDs = source["agentIDs"];
	        this.actions = source["actions"];
	    }
	}
	
	export class TSResourceState {
	    resourceIDs: string[];
	    resourceStates: number[];
	
	    static createFrom(source: any = {}) {
	        return new TSResourceState(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.resourceIDs = source["resourceIDs"];
	        this.resourceStates = source["resourceStates"];
	    }
	}
	export class TSExperimentResult {
	    resourceStates: TSResourceState[];
	    actionList: TSActionList[];
	
	    static createFrom(source: any = {}) {
	        return new TSExperimentResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.resourceStates = this.convertValues(source["resourceStates"], TSResourceState);
	        this.actionList = this.convertValues(source["actionList"], TSActionList);
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}

}

export namespace mra {
	
	export class MRA {
	    id: string;
	    agents: proto.Agent[];
	    resources: string[];
	
	    static createFrom(source: any = {}) {
	        return new MRA(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.id = source["id"];
	        this.agents = this.convertValues(source["agents"], proto.Agent);
	        this.resources = source["resources"];
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}

}

export namespace proto {
	
	export enum SynthesisAlgorithm {
	    COLLECTIVE = 0,
	    NASH_EQUILIBRIUM = 1,
	    EPSILON_NASH_EQUILIBRIUM = 2,
	}
	export class Agent {
	    id?: string;
	    demand?: number;
	    acc?: string[];
	
	    static createFrom(source: any = {}) {
	        return new Agent(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.id = source["id"];
	        this.demand = source["demand"];
	        this.acc = source["acc"];
	    }
	}
	export class MRA {
	    id?: string;
	    agents?: Agent[];
	    resources?: string[];
	
	    static createFrom(source: any = {}) {
	        return new MRA(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.id = source["id"];
	        this.agents = this.convertValues(source["agents"], Agent);
	        this.resources = source["resources"];
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}

}

