import { create } from "zustand";
import { experiment } from "../../wailsjs/wailsjs/go/models";
import { RetrieveMetadata } from "../../wailsjs/wailsjs/go/main/App";

export type ExperimentMetadataState = {
    experimentMetadata: Array<experiment.Metadata>
    fetchAllMetadata: () => Promise<Array<experiment.Metadata>>
}

const useExperimentMetadata = create<ExperimentMetadataState>((set) => ({
    experimentMetadata: new Array<experiment.Metadata>(),
    fetchAllMetadata: async () => {
        return await RetrieveMetadata();
    }
}))