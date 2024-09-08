import { BaseEdge, EdgeLabelRenderer, getBezierPath } from "@xyflow/react";

const Edge = ({
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    data,
}: any) => {
    const [edgePath, labelX, labelY] = getBezierPath({
        sourceX,
        sourceY,
        sourcePosition,
        targetX,
        targetY,
        targetPosition,
    });

    console.log("RENDER EDGE!")

    return (
        <>
            <BaseEdge id={id} path={edgePath} />
            <EdgeLabelRenderer>
                <div
                    style={{
                        position: 'absolute',
                        transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
                        padding: 10,
                        borderRadius: 5,
                        fontSize: 12,
                        fontWeight: 700,
                    }}
                    className="nodrag nopan text-primary-foreground bg-primary"
                >
                    {data ? data.label : ""}
                </div>
            </EdgeLabelRenderer>
        </>
    )
};

export default Edge;