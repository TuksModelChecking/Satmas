import { proto } from "@/wailsjs/wailsjs/go/models";

export type Parameters = {
    numberOfIterations: number;
    timebound: number;
    algorithm: proto.SynthesisAlgorithm;
}

export const createParameters = (set: any) => ({
    numberOfIterations: Number,
    timebound: Number,
    algorithm: proto,
    setParameters: (newParameters: Parameters) => set({ parameters: newParameters }),
})