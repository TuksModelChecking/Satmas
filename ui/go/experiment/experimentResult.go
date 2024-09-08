package experiment

type TSResourceState struct {
	ResourceIDs    []string `json:"resourceIDs"`
	ResourceStates []int    `json:"resourceStates"`
}

type TSActionList struct {
	AgentIDs []int    `json:"agentIDs"`
	Actions  []string `json:"actions"`
}

type TSExperimentResult struct {
	ResourceStates []TSResourceState `json:"resourceStates"`
	ActionList     []TSActionList    `json:"actionList"`
}
