import {
  LifeBuoy,
  Play,
  SquareTerminal,
  SquareUser,
  Triangle,
} from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import MRA from "./mra"
import Parameters from "./parameters"
import Message from "./message"
import Sidebar from "./sidebar"

export function Dashboard() {
  return (
    <div className="grid h-screen w-full pl-[56px]">
      <Sidebar />
      <div className="flex flex-col">
        <header className="sticky top-0 z-10 flex h-[57px] items-center justify-between gap-1 border-b bg-background px-4">
          <h1 className="text-xl font-semibold">Experiment Runner</h1>
          <Button>
            <Play className="mr-2 h-4 w-4" /> Run Experiment
          </Button>
        </header>
        <main className="grid flex-1 gap-4 overflow-auto p-4 md:grid-cols-2 lg:grid-cols-3">
          <div
            className="relative hidden flex-col items-start gap-8 md:flex"
          >
            <form className="grid w-full items-start gap-6">
              <Parameters />
              <Message />
            </form>
          </div>
          <div className="relative flex min-h-[100px] flex-col rounded-xl bg-muted/50 p-4 lg:col-span-2">
            <Badge variant="outline" className="absolute right-3 top-3">
              MRA
            </Badge>
            <div className="w-[100vw] h-[100vh]">
              <MRA />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default Dashboard;