interface Confusion {
    truePositives: number;
    falsePositives: number;
    trueNegatives: number;
    falseNegatives: number;
}
export declare function computeConfusion(actualValues: boolean[], assignedValues: boolean[]): Confusion;
export {};
