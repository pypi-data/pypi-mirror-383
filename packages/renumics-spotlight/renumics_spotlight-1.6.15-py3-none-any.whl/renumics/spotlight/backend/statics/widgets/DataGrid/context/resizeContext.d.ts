import * as React from 'react';
import { MutableRefObject } from 'react';
type EditingContextState = {
    getColumnWidth: (index: number) => number;
    startResizing: (columnIndex: number) => void;
    resizedIndex: MutableRefObject<number | undefined>;
};
export declare const ResizingContext: React.Context<EditingContextState>;
interface Props {
    children: React.ReactNode;
    onResize: (columnIndex: number) => void;
}
export declare const ColumnResizeProvider: ({ children, onResize }: Props) => JSX.Element;
export {};
