import { ConnectionMode, MarkerType, Position, ReactFlow, addEdge, useEdgesState, useNodesState, useReactFlow } from "@xyflow/react";
import { Toaster, toast } from "sonner";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuShortcut,
  ContextMenuTrigger,
} from "@/components/ui/context-menu"
import Node from "./node";
import { useHotkeys } from 'react-hotkeys-hook';
import { useCallback } from "react";
import Edge from "./edge";
import '@xyflow/react/dist/style.css';
import useExperimentState from "@/lib/experiment/experimentState";
import { proto } from "../../wailsjs/wailsjs/go/models";

const nodeTypes = {
  custom: Node,
};

const edgeTypes = {
  floating: Edge,
};

let nodeID = 1;
const getNodeID = () => `${nodeID++}`;

let agentID = 1;
const getAgentID = () => `${agentID++}`;

let resourceID = 1;
const getResourceID = () => `${resourceID++}`

const proOptions = { hideAttribution: true };
const defaultEdgeOptions = {
  style: { strokeWidth: 3, stroke: "black" },
  type: 'floating',
  markerEnd: {
    type: MarkerType.ArrowClosed,
    color: "black",
  },
};

const MRA = () => {
  const addAgentToState = useExperimentState((state) => state.addAgent);
  const removeAgentFromState = useExperimentState((state) => state.removeAgent);
  const addResourceToState = useExperimentState((state) => state.addResource);
  const removeResourceFromState = useExperimentState((state) => state.removeResource);
  const addResourcesAccess = useExperimentState((state) => state.addResourceAccess);

  const { screenToFlowPosition, getViewport } = useReactFlow();
  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);

  useHotkeys('ctrl+a', () => { addAgent() })
  useHotkeys('ctrl+r', () => { addResource() })

  const createNode = (data: { isAgent: boolean, id: string }) => {
    return {
      id: getNodeID(),
      type: "custom",
      data: data,
      position: screenToFlowPosition({
        x: getViewport().x,
        y: getViewport().y,
      }),
      className: "max-w-[100px]",
    };
  }

  const addAgent = () => {
    const agentID = getAgentID();
    addAgentToState(new proto.Agent({
      id: agentID,
      demand: 0,
      acc: [],
    }));
    setNodes((nds) => {
      return [...nds, createNode({ isAgent: true, id: agentID })]
    });
  }

  const addResource = () => {
    const resourceID = getResourceID();
    addResourceToState(resourceID);
    setNodes((nds) => {
      return [...nds, createNode({ isAgent: false, id: resourceID })]
    });
  }

  const onConnect = useCallback(
    (params: any) =>
      setEdges((eds) => {
        const source = params.sourceHandle.split("_");
        const target = params.targetHandle.split("_");
        if (source[1] === target[1]) { // Connecting Agent <-> Agent or Resource <-> Resource
          toast.error("Invalid Connection", {
            description: "Can only connect agents to resources",
          })
          return eds;
        } else if (source[1] === 'R' && target[1] === 'A') { // swap if source and targets are not as expected
          // swap source and target
          const temp = params.source;
          params.source = params.target;
          params.target = temp;
          const tempHandle = params.sourceHandle;
          params.sourceHandle = params.targetHandle;
          params.targetHandle = tempHandle;
        }

        // register resource access
        addResourcesAccess(source[0], target[0]);

        // add edge for view
        return addEdge(
          {
            ...params,
            type: 'floating',
            markerEnd: { type: MarkerType.Arrow },
          },
          eds,
        );
      }),
    [],
  );

  const onNodeDelete = useCallback((nodes: any) => {
    nodes.forEach((node: any) => {
      if (node.data.isAgent) {
        removeAgentFromState(node.data.id);
      } else {
        removeResourceFromState(node.data.id);
      }
    })
  }, []);

  return (
    <ContextMenu>
      <ContextMenuTrigger>
        <div className="h-full w-full">
          <Toaster />
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodesDelete={onNodeDelete}
            connectionMode={ConnectionMode.Loose}
            fitView
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            defaultEdgeOptions={defaultEdgeOptions}
            proOptions={proOptions}
          >
          </ReactFlow>
        </div>
      </ContextMenuTrigger>
      <ContextMenuContent className="w-64">
        <ContextMenuItem inset onClick={addAgent}>
          Add Agent
          <ContextMenuShortcut>Ctrl+a</ContextMenuShortcut>
        </ContextMenuItem>
        <ContextMenuItem inset onClick={addResource}>
          Add Resource
          <ContextMenuShortcut>Ctrl+r</ContextMenuShortcut>
        </ContextMenuItem>
        <ContextMenuItem inset>
          Clear
          <ContextMenuShortcut>Ctrl+R</ContextMenuShortcut>
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  )
};

export default MRA;