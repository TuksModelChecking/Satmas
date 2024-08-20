import { mra } from "@/wailsjs/wailsjs/go/models";
import { ColumnDef } from "@tanstack/react-table";

export const columns: ColumnDef<mra.MRA>[] = [
    {
        accessorKey: "id",
        header: "ID",
    },
    {
        accessorKey: "agents",
        header: "No. Agents",
        accessorFn: row => `${row.agents.length}`
    },
    {
        accessorKey: "resources",
        header: "No. Resources",
        accessorFn: row => `${row.resources.length}`
    },
];