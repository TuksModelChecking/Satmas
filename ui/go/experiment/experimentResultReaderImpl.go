package experiment

import (
	"fmt"

	"github.com/wailsapp/wails/v2/pkg/logger"
)

type ExperimentResultReaderImpl struct {
	logger logger.Logger
	store  *Store
}

func NewExperimentResultReaderImpl(
	logger logger.Logger,
	store *Store,
) *ExperimentResultReaderImpl {
	return &ExperimentResultReaderImpl{
		logger: logger,
		store:  store,
	}
}

func (e *ExperimentResultReaderImpl) ReadExperimentResult(experimentID string) (*TSExperimentResult, error) {
	experimentResult, err := e.store.RetrieveResult(experimentID)
	if err != nil {
		e.logger.Error(
			fmt.Sprintf("error retrieving experiment result for experiment %s: %s", experimentID, err.Error()),
		)
		return nil, fmt.Errorf("error retrieving experiment result: %w", err)
	}

	resourceStatesMap := []TSResourceState{}
	for _, v := range experimentResult.ResourceStates {
		resourceStatesAtTimestep := []int{}
		for _, state := range v.ResourceStates {
			resourceStatesAtTimestep = append(resourceStatesAtTimestep, int(state))
		}

		resourceStatesMap = append(resourceStatesMap, TSResourceState{
			ResourceIDs:    v.ResourceIDs,
			ResourceStates: resourceStatesAtTimestep,
		})
	}

	agentActionsMap := []TSActionList{}
	for _, v := range experimentResult.ActionList {
		agentIDs := []int{}
		for _, agentID := range v.AgentIDs {
			agentIDs = append(agentIDs, int(agentID))
		}

		agentActionsMap = append(agentActionsMap, TSActionList{
			AgentIDs: agentIDs,
			Actions:  v.Actions,
		})
	}

	return &TSExperimentResult{
		ResourceStates: resourceStatesMap,
		ActionList:     agentActionsMap,
	}, nil
}
