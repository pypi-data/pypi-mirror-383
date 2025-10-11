import { Problem } from '../types';
declare function useCell(columnKey: string, row: number, fetchDelay?: number): [unknown | null | undefined, Problem | undefined];
export declare function useRow(row: number, columnKeys: Array<string>, fetchDelay?: number): [Record<string, unknown> | undefined, Problem | undefined];
export default useCell;
