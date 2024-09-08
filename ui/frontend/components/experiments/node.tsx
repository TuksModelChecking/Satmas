import { Handle, Position, useUpdateNodeInternals } from "@xyflow/react";
import { memo } from "react"

const Node = (props: any) => {
    const updateNodeInternals = useUpdateNodeInternals();
    updateNodeInternals(props.data.id);
    return (
        <div className="relative text-center w-[200px] h-full rounded-full border-4 border-black border-solid flex items-center justify-center">
            <div>
                {props.data.content.split("\n").map((entry: string) => {
                    return <p key={`${props.data.id}-${entry}`}>{entry}</p>
                })}
            </div>
            {props.data.id !== '0' &&
                <Handle position={Position.Top} type="target" id={`t-handle-${props.data.id}`} />
            }
            <Handle position={Position.Bottom} type="source" id={`b-handle-${props.data.id}`} />
        </div>
    )
}

export default memo(Node);