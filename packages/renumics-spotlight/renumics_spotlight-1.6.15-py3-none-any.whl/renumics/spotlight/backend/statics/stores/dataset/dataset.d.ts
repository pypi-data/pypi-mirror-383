import { DataType } from '../../datatypes';
import { TransferFunction } from '../../hooks/useColorTransferFunction';
import { ColumnsStats, DataColumn, DataRow, DataIssue as DataIssue, Filter, IndexArray, TableData, Problem } from '../../types';
export type CallbackOrData<T> = ((data: T) => T) | T;
export type Sorting = 'DESC' | 'ASC';
export type DataSelector = 'full' | 'filtered' | 'selected';
export interface Dataset {
    uid?: string;
    generationID: number;
    filename?: string;
    loading: boolean;
    loadingError?: Problem;
    columnStats: {
        full: ColumnsStats;
        selected: ColumnsStats;
        filtered: ColumnsStats;
    };
    columns: DataColumn[];
    columnsByKey: Record<string, DataColumn>;
    columnData: TableData;
    isAnalysisRunning: boolean;
    issues: DataIssue[];
    rowsWithIssues: IndexArray;
    colorTransferFunctions: Record<string, {
        full: TransferFunction;
        filtered: TransferFunction;
    }>;
    recomputeColorTransferFunctions: () => void;
    length: number;
    indices: Int32Array;
    getRow: (index: number) => DataRow;
    isIndexSelected: boolean[];
    selectedIndices: Int32Array;
    isIndexHighlighted: boolean[];
    highlightedIndices: Int32Array;
    isIndexFiltered: boolean[];
    filteredIndices: Int32Array;
    sortColumns: Map<DataColumn, Sorting>;
    sortBy: (column?: DataColumn, sorting?: Sorting) => void;
    columnRelevance: Map<string, number>;
    columnRelevanceGeneration: number;
    filters: Filter[];
    tags: string[];
    lastFocusedRow?: number;
    openTable: (path: string) => void;
    fetch: () => void;
    refetchColumnValues: (columnKey: string) => void;
    fetchIssues: () => void;
    refresh: () => void;
    addFilter: (filter: Filter) => void;
    removeFilter: (filter: Filter) => void;
    toggleFilterEnabled: (filter: Filter) => void;
    replaceFilter: (filter: Filter, newFilter: Filter) => void;
    selectRows: (rows: CallbackOrData<IndexArray>) => void;
    setHighlightedRows: (mask: boolean[]) => void;
    highlightRowAt: (rowIndex: number, only?: boolean) => void;
    highlightRows: (rows: CallbackOrData<IndexArray>) => void;
    dehighlightRowAt: (rowIndex: number) => void;
    dehighlightAll: () => void;
    relevanceWorker: any;
    isComputingRelevance: boolean;
    recomputeColumnRelevance: () => void;
    focusRow: (row?: number) => void;
    clearLoadingError: () => void;
}
export declare function convertValue(value: any, type: DataType): any;
export declare const useDataset: import("zustand").UseBoundStore<Omit<import("zustand").StoreApi<Dataset>, "subscribe"> & {
    subscribe: {
        (listener: (selectedState: Dataset, previousSelectedState: Dataset) => void): () => void;
        <U>(selector: (state: Dataset) => U, listener: (selectedState: U, previousSelectedState: U) => void, options?: {
            equalityFn?: ((a: U, b: U) => boolean) | undefined;
            fireImmediately?: boolean | undefined;
        } | undefined): () => void;
    };
}>;
