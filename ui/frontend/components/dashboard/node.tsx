import { memo, useState } from "react";
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import {
    ContextMenu,
    ContextMenuContent,
    ContextMenuItem,
    ContextMenuTrigger,
} from "@/components/ui/context-menu"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Handle, Position } from "@xyflow/react";
import useExperimentState from "@/lib/experiment/experimentState"

const Node = (props: any) => {
    const setAgentDemand = useExperimentState((state) => state.setAgentDemand);
    const [openDialog, setOpenDialog] = useState(false);
    const [demand, setDemand] = useState(0);

    const handleDemandSubmission = () => {
        if (props.data.isAgent) {
            setAgentDemand(props.data.id, demand);
        }
        setOpenDialog(!openDialog);
    };

    return (
        <Dialog open={openDialog} onOpenChange={() => setOpenDialog(!openDialog)}>
            <ContextMenu>
                <ContextMenuTrigger>
                    <div className="text-center w-[100px] h-[100px] rounded-full border-4 border-black border-solid flex items-center justify-center">
                        <span className="text-3xl">{props.data.isAgent ? "A" : "R"}{demand > 0 ? `: ${demand}` : ""}</span>
                        <Handle position={Position.Left} type="source" id={props.data.id + "_" + (props.data.isAgent ? "A" : "R") + "_l"} />
                        <Handle position={Position.Bottom} type="source" id={props.data.id + "_" + (props.data.isAgent ? "A" : "R") + "_b"} />
                        <Handle position={Position.Right} type="source" id={props.data.id + "_" + (props.data.isAgent ? "A" : "R") + "_r"} />
                        <Handle position={Position.Top} type="source" id={props.data.id + "_" + (props.data.isAgent ? "A" : "R") + "_t"} />
                    </div>
                </ContextMenuTrigger>
                {props.data.isAgent &&
                    <ContextMenuContent>
                        <DialogTrigger asChild>
                            <ContextMenuItem>
                                <span>Add Demand</span>
                            </ContextMenuItem>
                        </DialogTrigger>
                    </ContextMenuContent>
                }
            </ContextMenu>
            <DialogContent aria-describedby="agent demand">
                <DialogHeader>
                    <DialogTitle>Add Demand To Agent</DialogTitle>
                    <DialogDescription>
                        <div className="flex justify-start items-center gap-4 mt-4">
                            <Label htmlFor={"demand" + props.data.id} className="text-right">
                                Demand
                            </Label>
                            <Input
                                id={"demand" + props.data.id}
                                type="number"
                                defaultValue="0"
                                className="col-span-3"
                                value={demand}
                                onChange={(e) => setDemand(Number(e.target.value))}
                            />
                        </div>
                    </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                    <Button type="submit" onClick={handleDemandSubmission}>Confirm</Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
};

export default memo(Node);