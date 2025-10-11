import { IndexArray } from '../types';
export declare const umapMetricNames: readonly ["euclidean", "standardized euclidean", "robust euclidean", "cosine", "mahalanobis"];
export type UmapMetric = (typeof umapMetricNames)[number];
export declare const pcaNormalizations: readonly ["none", "standardize", "robust standardize"];
export type PCANormalization = (typeof pcaNormalizations)[number];
interface ReductionResult {
    points: [number, number][];
    indices: IndexArray;
}
export declare class DataService {
    computeUmap(widgetId: string, columnNames: string[], indices: IndexArray, n_neighbors: number, metric: UmapMetric, min_dist: number): Promise<ReductionResult>;
    computePCA(widgetId: string, columnNames: string[], indices: IndexArray, pcaNormalization: PCANormalization): Promise<ReductionResult>;
}
declare const dataService: DataService;
export default dataService;
