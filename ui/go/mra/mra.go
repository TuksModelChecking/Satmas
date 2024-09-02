package mra

import (
	"ui/go/codegen/ui/proto"

	"github.com/google/uuid"
)

type MRA struct {
	ID        string         `json:"id"`
	Agents    []*proto.Agent `json:"agents"`
	Resources []string       `json:"resources"`
}

func NewMRA(agents []*proto.Agent, resources []string) *MRA {
	return &MRA{
		ID:        uuid.NewString(),
		Agents:    agents,
		Resources: resources,
	}
}
