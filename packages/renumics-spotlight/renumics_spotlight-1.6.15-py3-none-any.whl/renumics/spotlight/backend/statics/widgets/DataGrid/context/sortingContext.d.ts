import * as React from 'react';
import { FunctionComponent } from 'react';
import { Sorting } from '../../../stores/dataset';
type SortingContextState = {
    sorting: [string, Sorting][];
    setSorting: React.Dispatch<React.SetStateAction<[string, Sorting][]>>;
    sortedIndices: Int32Array;
    getOriginalIndex: (sortedIndex: number) => number;
    getSortedIndex: (originalIndex: number) => number;
};
export declare const SortingContext: React.Context<SortingContextState>;
export declare const SortingProvider: FunctionComponent<Pick<SortingContextState, 'sorting' | 'setSorting'> & {
    children: React.ReactNode;
}>;
export declare const useSortings: () => [string, Sorting][];
export declare const useSortByColumn: (columnKey: string) => [Sorting | undefined, (sorting?: Sorting | undefined) => void, () => void];
export {};
