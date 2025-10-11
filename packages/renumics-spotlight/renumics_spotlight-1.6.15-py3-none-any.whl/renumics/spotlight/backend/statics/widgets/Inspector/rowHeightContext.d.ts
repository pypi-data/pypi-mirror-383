import { FunctionComponent, ReactNode } from 'react';
type RowHeightContextState = {
    startResize: (index: number, screenY: number) => void;
    rowHeight: (index: number) => number;
};
export declare const RowHeightContext: import("react").Context<RowHeightContextState>;
type RowHeightProviderProps = {
    onResize?: (resizedView: string) => void;
    children?: ReactNode;
};
declare const RowHeightProvider: FunctionComponent<RowHeightProviderProps>;
export default RowHeightProvider;
