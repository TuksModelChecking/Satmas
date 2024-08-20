import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

const Message = () => {
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
                    className="min-h-[9.5rem]"
                />
            </div>
        </fieldset>
    );
};

export default Message;