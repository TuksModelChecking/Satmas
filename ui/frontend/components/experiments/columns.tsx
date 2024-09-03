import { experiment } from "@/wailsjs/wailsjs/go/models";
import { ColumnDef } from "@tanstack/react-table";
import { Loader2 } from "lucide-react";

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
                return <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            } else if (row.original.state === "Successful") {
                return <p className="text-primary">{row.original.state}</p>
            } else if (row.original.state === "Failed") {
                return <p className="text-red-500">{row.original.state}</p>
            } else {
                <p>{row.original.state}</p>
            }
        }
    },
];