import { TransferFunction } from '../../hooks/useColorTransferFunction';
import { DataColumn, TableData } from '../../types';
type ColumnsTransferFunctions = Record<string, {
    full: TransferFunction;
    filtered: TransferFunction;
}>;
export declare const makeColumnsColorTransferFunctions: (columns: DataColumn[], data: TableData, filteredIndices: Int32Array) => ColumnsTransferFunctions;
export {};
