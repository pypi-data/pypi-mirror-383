import * as React from 'react';
import type { ListOnScrollProps } from 'react-window';
type Props = {
    height: number;
    width: number;
    itemCount: number;
    onScroll: (props: ListOnScrollProps) => void;
};
export type Ref = {
    scrollTo: (scrollTo: number) => void;
    scrollToItemBottom: (index: number) => void;
    resetAfterIndex: (index: number) => void;
};
declare const _default: React.ForwardRefExoticComponent<Props & React.RefAttributes<Ref>>;
export default _default;
