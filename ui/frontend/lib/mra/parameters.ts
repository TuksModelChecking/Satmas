export type Parameters = {
    numberOfIterations: number;
    timebound: number;
    algorithm: AlgorithmType;
}

export enum AlgorithmType {
    COLLECTIVE,
    NASH,
    EPSILON,
}

export enum ExperimentExecutionState {
    DRAFT,
    PENDING,
    RUNNING,
    SUCCESSFUL,
    FAILED
}

export const createParameters = (set: any) => ({
    numberOfIterations: Number,
    timebound: Number,
    algorithm: AlgorithmType,
    setParameters: (newParameters: Parameters) => set({ parameters: newParameters }),
})