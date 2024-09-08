import { ReactNode, useCallback, useEffect, useState } from "react";
import { ReadExperimentResult } from "@/wailsjs/wailsjs/go/main/App";
import { toast } from "sonner";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "../ui/sheet";
import { experiment } from "@/wailsjs/wailsjs/go/models";
import Node from "./node";
import { Connection, ConnectionMode, MarkerType, ReactFlow, ReactFlowProvider, addEdge, useEdgesState, useNodesState, useReactFlow, Edge as FlowEdge } from "@xyflow/react";
import Edge from "./edge";

interface ResultProps {
    experimentID: string;
    children: ReactNode;
}


const proOptions = { hideAttribution: true };

const nodeTypes = {
    custom: Node,
}

const edgeTypes = {
    floating: Edge,
};

const defaultEdgeOptions = {
    style: { strokeWidth: 3, stroke: "black" },
    type: 'floating',
    markerEnd: {
        type: MarkerType.ArrowClosed,
        color: "black",
    },
};

const Result = ({ experimentID, children }: ResultProps) => {
    let nodeID = 0;
    const getNodeID = () => `${nodeID++}`;
    const { screenToFlowPosition, getViewport } = useReactFlow();
    const [open, setOpen] = useState(false);

    const createNodes = (resourceStates: Array<experiment.TSResourceState>) => {
        let states = resourceStates.map((state) => {
            return state.resourceIDs.map((id, idx) => {
                return `${id}: ${state.resourceStates[idx]}\n`
            }).join("\n")
        });

        return states.map((state) => {
            const nodeID = getNodeID();
            return {
                id: nodeID,
                type: "custom",
                data: {
                    content: `${state}`,
                    id: nodeID,
                },
                position: screenToFlowPosition({
                    x: getViewport().x,
                    y: getViewport().y + (Number(nodeID) * 10 * state.length),
                }),
                className: "max-w-[100px]",
            };
        })
    };

    const createEdges = (actionList: Array<experiment.TSActionList>) => {
        const edges = actionList.map((action, idx) => {
            const sourceID = idx
            let targetID = idx + 1
            const nodeID = getNodeID();
            if (targetID !== actionList.length) {
                return {
                    id: nodeID,
                    source: sourceID.toString(),
                    target: targetID.toString(),
                    sourceHandle: `b-handle-${sourceID}`,
                    targetHandle: `t-handle-${targetID}`,
                    data: {
                        label: action.actions.map((act, idx) => {
                            return `${action.agentIDs[idx]}: ${act}`;
                        }).join(" "),
                        id: nodeID,
                    },
                    type: "floating",
                };
            }
            return {
                id: nodeID,
                data: {
                    label: [],
                    id: nodeID,
                },
            };
        })

        console.log(edges);
        return edges;
    };

    const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);
    const onConnect = useCallback(
        (params: any) => setEdges((eds) => {
            console.log(params);
            return addEdge(
                {
                    ...params,
                    type: 'floating',
                    markerEnd: { type: MarkerType.Arrow },
                },
                eds,
            )
        }),
        [],
    );

    useEffect(() => {
        if (open) {
            (async () => {
                try {
                    const experimentResult = await ReadExperimentResult(experimentID);
                    setNodes(createNodes(experimentResult.resourceStates));
                    setEdges(createEdges(experimentResult.actionList));
                    console.log("CALLED SET: ", experimentResult.actionList.length)
                } catch (e) {
                    toast.error(
                        "error reading experiment result"
                    )
                } finally {
                }
            })()

        }
    }, [open]);

    return (
        <Sheet onOpenChange={() => setOpen(!open)}>
            <SheetTrigger asChild>
                {children}
            </SheetTrigger>
            <SheetContent side="bottom">
                <SheetHeader>
                    <SheetTitle>Path</SheetTitle>
                    <SheetDescription>Click and drag to view the entire path</SheetDescription>
                </SheetHeader>
                <div className="mt-3 h-[80vh] w-[90vw] bg-muted/50 rounded-xl">
                    <ReactFlowProvider key={experimentID}>
                        <ReactFlow
                            nodes={nodes}
                            nodeTypes={nodeTypes}
                            onNodesChange={onNodesChange}
                            edges={edges}
                            edgeTypes={edgeTypes}
                            onEdgesChange={onEdgesChange}
                            connectionMode={ConnectionMode.Loose}
                            onConnect={onConnect}
                            defaultEdgeOptions={defaultEdgeOptions}
                            proOptions={proOptions}
                            fitView
                        >
                        </ReactFlow>
                    </ReactFlowProvider>
                </div>
            </SheetContent>
        </Sheet>
    );
};

export default Result;