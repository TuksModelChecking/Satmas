import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useExperimentMetadata } from "@/lib/experiment/experimentExecutionState";
import useExperimentState, { ExperimentStateType } from "@/lib/experiment/experimentState";

const Message = () => {
    const message = useExperimentState((state: unknown) => (state as ExperimentStateType).message);
    const setMessage = useExperimentState((state: unknown) => (state as ExperimentStateType).setMessage);
    const updateMessage = (value: unknown) => {
        setMessage(value as string);
    };

    return (
        <fieldset className="grid gap-6 rounded-lg border p-4">
            <legend className="flex -ml-1 px-1 text-sm font-medium">
                Message
            </legend>
            <div className="grid gap-3">
                <Label htmlFor="content">Content</Label>
                <Textarea
                    id="content"
                    placeholder="Experiment to check..."
                    value={message}
                    className="min-h-[9.5rem]"
                    onChange={updateMessage}
                />
            </div>
        </fieldset>
    );
};

export default Message;