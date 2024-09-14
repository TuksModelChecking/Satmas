import { useState } from "react";
import useExperimentState from "./experimentState";
import { ReadOneExperiment } from "@/wailsjs/wailsjs/go/main/App";
import { experiment, proto } from "@/wailsjs/wailsjs/go/models";
import { toast } from "sonner";

const useLoadExperiment = (experimentID: string) => {
    const [loading, setLoading] = useState(false);
    const setExperiment = useExperimentState((state) => state.setExperiment);
    const readOneExperiment = async () => {
        setLoading(true);
        let request = new experiment.ReadOneExperimentRequest();
        request.experimentID = experimentID;
        try {
            const response = await ReadOneExperiment(
                request,
            )
            setExperiment(response.experiment);
        } catch (e) {
            console.error("error retrieving experiment");
            toast.error("error retrieving experiment");
        } finally {
            setLoading(false);
        }
    };
    return { loading, readOneExperiment };
};

export default useLoadExperiment;