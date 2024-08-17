import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Handle, Position } from "@xyflow/react";
import { memo } from "react";

const Node = (props: any) => {
    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                    <div className="text-center w-[100px] h-[100px] rounded-full border-4 border-black border-solid flex items-center justify-center">
                        <span className="text-3xl">{props.data.isAgent ? "A" : "R"}</span>
                        <Handle position={Position.Left} type="source" id={props.data.id + "_" + (props.data.isAgent ? "A" : "R") + "_l"} />
                        <Handle position={Position.Bottom} type="source" id={props.data.id + "_" + (props.data.isAgent ? "A" : "R") + "_b"} />
                        <Handle position={Position.Right} type="source" id={props.data.id + "_" + (props.data.isAgent ? "A" : "R") + "_r"} />
                        <Handle position={Position.Top} type="source" id={props.data.id + "_" + (props.data.isAgent ? "A" : "R") + "_t"} />
                    </div>
                </TooltipTrigger>
                <TooltipContent className="text-3xl">
                    {props.data.isAgent ? "Agent" : "Resource"}
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    )
};

export default memo(Node);