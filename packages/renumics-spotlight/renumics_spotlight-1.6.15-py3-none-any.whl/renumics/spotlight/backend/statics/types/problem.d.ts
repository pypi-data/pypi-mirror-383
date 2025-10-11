export interface Problem {
    type: string;
    title: string;
    detail?: string;
    instance?: string;
}
export declare function isProblem(error: unknown): error is Problem;
