import { Label } from "@/components/ui/label"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input";
import { Rabbit, Turtle, Bird } from "lucide-react";
import useExperimentState, { ExperimentStateType } from "@/lib/experiment/experimentState";
import { proto } from "@/wailsjs/wailsjs/go/models";

const Parameters = () => {
    const parameters = useExperimentState((state: unknown) => (state as ExperimentStateType).parameters);
    const setParameters = useExperimentState((state: unknown) => (state as ExperimentStateType).setParameters);

    const updateAlgorithm = (value: unknown) => {
        setParameters({
            ...parameters,
            algorithm: value as proto.SynthesisAlgorithm,
        });
    };

    const updateNumberOfIterations = (value: unknown) => {
        setParameters({
            ...parameters,
            numberOfIterations: value as number,
        });
    };

    const updateNumberOfTimeBound = (value: unknown) => {
        setParameters({
            ...parameters,
            timebound: value as number,
        });
    };

    return (
        <fieldset className="grid gap-6 rounded-lg border p-4">
            <legend className="-ml-1 px-1 text-sm font-medium">
                Parameters
            </legend>
            <div className="grid gap-3">
                <Label htmlFor="model">Synthesis Algorithm</Label>
                <Select defaultValue={parameters.algorithm.toString()} onValueChange={updateAlgorithm}>
                    <SelectTrigger
                        id="model"
                        className="items-start [&_[data-description]]:hidden"
                    >
                        <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value={proto.SynthesisAlgorithm.COLLECTIVE.toString()}>
                            <div className="flex items-start gap-3 text-muted-foreground">
                                <Rabbit className="size-5" />
                                <div className="grid gap-0.5">
                                    <p>
                                        Collectively{" "}
                                        <span className="font-medium text-foreground">
                                            Optimal
                                        </span>
                                    </p>
                                    <p className="max-w-[300px] text-xs" data-description>
                                        Synthesises a collectively optimal strategy for all the agents working as the grand coalition.
                                    </p>
                                </div>
                            </div>
                        </SelectItem>
                        <SelectItem value={proto.SynthesisAlgorithm.NASH_EQUILIBRIUM.toString()}>
                            <div className="flex items-start gap-3 text-muted-foreground">
                                <Turtle className="size-5" />
                                <div className="grid gap-0.5">
                                    <p>
                                        Nash{" "}
                                        <span className="font-medium text-foreground">
                                            Equilibrium
                                        </span>
                                    </p>
                                    <p className="max-w-[300px] text-xs" data-description>
                                        Synthesises a strategy profile such that it forms a Nash Equilibrium.
                                    </p>
                                </div>
                            </div>
                        </SelectItem>
                        <SelectItem value={proto.SynthesisAlgorithm.EPSILON_NASH_EQUILIBRIUM.toString()}>
                            <div className="flex items-start gap-3 text-muted-foreground">
                                <Bird className="size-5" />
                                <div className="grid gap-0.5">
                                    <p>
                                        Epsilon-Nash{" "}
                                        <span className="font-medium text-foreground">
                                            Equilibrium
                                        </span>
                                    </p>
                                    <p className="max-w-[300px] text-xs" data-description>
                                        Synthesises a strategy profile such it form an epsilon Nash Equilbrium with a minimum epsilon value.
                                    </p>
                                </div>
                            </div>
                        </SelectItem>
                    </SelectContent>
                </Select>
            </div>
            <div className="grid grid-cols-2 gap-3">
                <div>
                    <Label htmlFor="iterations">Number Of Iterations</Label>
                    <Input id="iterations" type="number" placeholder="10" disabled={parameters.algorithm.toString() !== proto.SynthesisAlgorithm.EPSILON_NASH_EQUILIBRIUM.toString()} defaultValue={parameters.numberOfIterations} onChange={(e) => updateNumberOfIterations(e.target.value)} />
                </div>
                <div>
                    <Label htmlFor="timebound">Timebound (K)</Label>
                    <Input id="timebound" type="number" placeholder="5" defaultValue={parameters.timebound} onChange={(e) => updateNumberOfTimeBound(e.target.value)} />
                </div>
            </div>
        </fieldset >
    );
};

export default Parameters;