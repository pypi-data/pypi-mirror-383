import * as React from 'react';
import { FunctionComponent } from 'react';
import { TableView } from '../../../types';
type RowContextState = {
    tableView: TableView;
    setTableView: (tableView: TableView) => void;
};
export declare const TableViewProvider: FunctionComponent<RowContextState & {
    children: React.ReactNode;
}>;
export declare const useTableView: () => RowContextState;
export {};
