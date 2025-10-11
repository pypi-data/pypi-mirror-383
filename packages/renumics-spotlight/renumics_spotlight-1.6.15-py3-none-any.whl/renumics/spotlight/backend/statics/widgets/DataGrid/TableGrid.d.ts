/// <reference types="react" />
import type { GridProps } from 'react-window';
interface Props {
    width: number;
    height: number;
    onScroll: GridProps['onScroll'];
}
export type Ref = {
    resetAfterColumnIndex: (index: number) => void;
};
declare const _default: import("react").ForwardRefExoticComponent<Props & import("react").RefAttributes<Ref>>;
export default _default;
