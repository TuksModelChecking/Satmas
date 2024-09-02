import { experiment } from "@/wailsjs/wailsjs/go/models";
import { ColumnDef } from "@tanstack/react-table";

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
            return <p>{row.original.state}</p>
        }
    },
];