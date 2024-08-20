package experiment

import "ui/go/codegen/ui/proto"

var AllSynthesisAlgorithms = []struct {
	Value  proto.SynthesisAlgorithm
	TSName string
}{
	{proto.SynthesisAlgorithm_COLLECTIVE, "COLLECTIVE"},
	{proto.SynthesisAlgorithm_NASHEQUILIBRIUM, "NASH_EQUILIBRIUM"},
	{proto.SynthesisAlgorithm_EPSILONNASHEQUILIBRIUM, "EPSILON_NASH_EQUILIBRIUM"},
}
