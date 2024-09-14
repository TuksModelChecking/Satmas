import { experiment } from "@/wailsjs/wailsjs/go/models";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpFromLine, Check, EllipsisVertical, Loader2, X } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "../ui/dropdown-menu";
import Result from "./result";
import Settings from "../appSettings/settings";
import { TooltipContent, TooltipProvider, TooltipTrigger } from "@radix-ui/react-tooltip";
import { Tooltip } from "../ui/tooltip";
import { Button } from "../ui/button";
import useLoadExperiment from "@/lib/experiment/experimentLoader";

export const columns: ColumnDef<experiment.Metadata>[] = [
    {
        accessorKey: "id",
        header: "ID",
        accessorFn: row => `${row.id.substring(0, 4)}...`
    },
    {
        accessorKey: "numberOfAgents",
        header: "No. Agents",
        accessorFn: row => `${row.numberOfAgents}`
    },
    {
        accessorKey: "numberOfResources",
        header: "No. Resources",
        cell: ({ cell, row }) => {
            return <p>{`${row.original.numberOfResources}`}</p>;
        }
    },
    {
        accessorKey: "state",
        header: "State",
        cell: ({ cell, row }) => {
            const { loading, readOneExperiment } = useLoadExperiment(row.original.id);
            if (row.original.state === "Pending") {
                return <Loader2 className="mx-2 h-4 w-4 animate-spin" />
            } else if (row.original.state === "Successful") {
                return (
                    <div className="flex items-center">
                        <Check className="mx-2 h-4 w-4 text-primary" />
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <ArrowUpFromLine onClick={async () => { await readOneExperiment() }} className="mx-2 h-4 w-4 cursor-pointer" />
                                </TooltipTrigger>
                                <TooltipContent side="top" sideOffset={5} className="bg-white p-3 shadow-sm rounded-lg">
                                    Load Experiment
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                        <Result state={row.original.state} experimentID={row.original.id}>
                            <EllipsisVertical className="mr-2 h-4 w-4 cursor-pointer" />
                        </Result>
                    </div>
                )
            } else if (row.original.state === "Failed") {
                return (
                    <div className="flex items-center">
                        <X className="mx-2 h-4 w-4 text-destructive" />
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <ArrowUpFromLine onClick={async () => { await readOneExperiment() }} className="mx-2 h-4 w-4 cursor-pointer" />
                                </TooltipTrigger>
                                <TooltipContent side="top" sideOffset={5} className="bg-white p-3 shadow-sm rounded-lg">
                                    Experiment Runner
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                        <Result state={row.original.state} experimentID={row.original.id}>
                            <EllipsisVertical className="mr-2 h-4 w-4 cursor-pointer" />
                        </Result>
                    </div>
                )
            } else {
                <p>{row.original.state}</p>
            }
        }
    }
];