import {
  LifeBuoy,
  Loader2,
  Play,
  Save,
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
import { AddExperiment, GenerateMRA } from "../../wailsjs/wailsjs/go/main/App";
import useExperimentState from "@/lib/experiment/experimentState"
import { Toaster, toast } from "sonner"
import { useState } from "react"
import { columns } from "../experiments/columns"
import ExperimentTable from "../experiments/table"
import { experiment } from "@/wailsjs/wailsjs/go/models"

export function Dashboard() {
  const agents = useExperimentState((state) => state.agents);
  const resources = useExperimentState((state) => state.resources);
  const parameters = useExperimentState((state) => state.parameters);
  const [submittingExperiment, setSubmittingExperiment] = useState(false);

  const fetchMetadata = async () => {

  };

  const handleRunExperiment = async () => {
    setSubmittingExperiment(true);
    const listOfAgents = Array.from(agents.values());
    const listOfResources = Array.from(resources.values());

    try {
      const newMRA = await GenerateMRA(listOfAgents, listOfResources)
      const tsExperiment = new experiment.TSExperiment();
      tsExperiment.algorithm = parameters.algorithm.toString();
      console.log(parameters.algorithm);
      tsExperiment.numberOfIterations = parameters.numberOfIterations.toString();
      tsExperiment.timebound = parameters.timebound.toString();
      tsExperiment.mra = newMRA;
      await AddExperiment(tsExperiment);
    } catch (e) {
      toast.error(`Something went wrong trying to run the experiment: ${e}`);
    } finally {
      setSubmittingExperiment(false);
    }
  };

  return (
    <div className="grid h-[80vh] w-full pl-[56px]">
      <Toaster />
      <Sidebar />
      <div className="flex flex-col">
        <header className="sticky top-0 z-10 flex h-[57px] items-center justify-between gap-1 border-b bg-background px-4">
          <h1 className="text-xl font-semibold">Experiment Runner</h1>
          <div className="flex items-center gap-2">
            <Button variant="secondary">
              <Save className="mr-2 h-4 w-4" /> Save Experiment
            </Button>
            <Button onClick={handleRunExperiment} disabled={submittingExperiment}>
              {submittingExperiment ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />} Run Experiment
            </Button>
          </div>
        </header>
        <main className="grid flex-1 gap-4 overflow-auto p-4 md:grid-cols-2 lg:grid-cols-3">
          <div
            className="relative hidden flex-col items-start gap-8 md:flex"
          >
            <form className="grid w-full items-start gap-6">
              <Parameters />
              <Message />
              <ExperimentTable columns={columns} data={[]} />
            </form>
          </div>
          <div className="relative flex flex-col rounded-xl bg-muted/50 p-4 lg:col-span-2 overflow-hidden max-h-[75vh]">
            <Badge variant="outline" className="absolute right-3 top-3">
              MRA
            </Badge>
            <div className="w-[90vw] h-[100vh]">
              <MRA />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default Dashboard;