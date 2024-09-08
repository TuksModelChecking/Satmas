import { experiment } from "@/wailsjs/wailsjs/go/models";
import { ColumnDef } from "@tanstack/react-table";
import { Check, EllipsisVertical, Loader2, X } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "../ui/dropdown-menu";
import Result from "./result";
import Settings from "../appSettings/settings";

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
            if (row.original.state === "Pending") {
                return <Loader2 className="mx-2 h-4 w-4 animate-spin" />
            } else if (row.original.state === "Successful") {
                return (
                    <div className="flex items-center">
                        <Check className="mx-2 h-4 w-4 text-primary" />
                        <Result experimentID={row.original.id}>
                            <EllipsisVertical className="mr-2 h-4 w-4 cursor-pointer" />
                        </Result>
                    </div>
                )
            } else if (row.original.state === "Failed") {
                return <X className="mx-2 h-4 w-4 text-destructive" />
            } else {
                <p>{row.original.state}</p>
            }
        }
    }
];