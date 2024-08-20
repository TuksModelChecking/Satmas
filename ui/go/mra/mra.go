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

// Not adding as member function to prevent exposing to UI
func ToProtoType(mra *MRA) *proto.MRA {
	protoAgents := []*proto.Agent{}
	for _, agent := range mra.Agents {
		protoAgents = append(protoAgents, &proto.Agent{
			Id:     agent.Id,
			Demand: agent.Demand,
			Acc:    agent.Acc,
		})
	}

	return &proto.MRA{
		Id:        mra.ID,
		Agents:    protoAgents,
		Resources: mra.Resources,
	}
}
