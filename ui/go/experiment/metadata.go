package experiment

import "time"

type Metadata struct {
	CreatedAt         time.Time `json:"createdAt"`
	ID                string    `json:"id"`
	NumberOfAgents    int       `json:"numberOfAgents"`
	NumberOfResources int       `json:"numberOfResources"`
	State             string    `json:"state"`
	PathToDefinition  string    `json:"pathToDefinition"`
	PathToResult      string    `json:"pathToResult"`
}
