import * as React from 'react';
import { FunctionComponent } from 'react';
import { CallbackOrData } from '../../../stores/dataset';
import { DataColumn } from '../../../types';
type ColumnContextState = {
    allColumns: DataColumn[];
    columns: DataColumn[];
    hideColumn: (columnKey: string) => void;
    setColumnKeys: (columns: CallbackOrData<string[]>) => void;
    areOrderedByRelevance: boolean;
    setAreOrderedByRelevance: (areOrderedByRelevance: boolean) => void;
    resetColumns: () => void;
};
export declare const ColumnContext: React.Context<ColumnContextState>;
type Props = {
    columnKeys: string[];
    setColumnKeys: (keys: CallbackOrData<string[]>) => void;
    areOrderedByRelevance: boolean;
    setAreOrderedByRelevance: (areOrderedByRelevance: boolean) => void;
    resetColumns: () => void;
};
export declare const ColumnProvider: FunctionComponent<Props & {
    children: React.ReactNode;
}>;
export declare const useOrderColumnsByRelevance: () => [
    ColumnContextState['areOrderedByRelevance'],
    ColumnContextState['setAreOrderedByRelevance']
];
export declare const useVisibleColumns: () => [
    ColumnContextState['columns'],
    ColumnContextState['setColumnKeys'],
    ColumnContextState['hideColumn'],
    ColumnContextState['resetColumns']
];
export declare const useColumn: (index: number) => DataColumn;
export declare const useColumns: () => DataColumn[];
export declare const useColumnCount: () => number;
export {};
