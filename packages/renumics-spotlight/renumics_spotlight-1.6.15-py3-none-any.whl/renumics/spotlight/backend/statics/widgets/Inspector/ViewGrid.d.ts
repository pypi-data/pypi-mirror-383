/// <reference types="react" />
import type { GridOnScrollProps } from 'react-window';
import { IndexArray } from '../../types';
import { LensConfig } from './types';
type ViewGridProps = {
    height: number;
    width: number;
    columnWidth: () => number;
    estimatedColumnWidth: number;
    views: LensConfig[];
    rowIndices: IndexArray;
    onScroll: ({ scrollUpdateWasRequested, scrollLeft, scrollTop, }: GridOnScrollProps) => void;
};
export type Ref = {
    scrollTo: ({ scrollLeft, scrollTop, }: {
        scrollLeft?: number | undefined;
        scrollTop?: number | undefined;
    }) => void;
    resetAfterRowIndex: (index: number) => void;
    resetAfterColumnIndex: (index: number) => void;
};
declare const _default: import("react").ForwardRefExoticComponent<ViewGridProps & import("react").RefAttributes<Ref>>;
export default _default;
