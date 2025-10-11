import { FunctionComponent } from 'react';
export interface Hint {
    type: 'warning';
    message: React.ReactNode;
}
export interface Props {
    title: string;
    selected?: string[];
    selectableColumns: string[];
    columnHints?: {
        [columnKey: string]: Hint;
    };
    onChangeColumn: (keys: string[]) => void;
}
declare const MultiColumnSelect: FunctionComponent<Props>;
export default MultiColumnSelect;
