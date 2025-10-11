import { DataColumn } from '../../lib';
import type { MatrixData } from './types';
export declare const useColumns: () => DataColumn[];
export declare function useData(xColumn?: DataColumn, yColumn?: DataColumn, filtered?: boolean): MatrixData;
