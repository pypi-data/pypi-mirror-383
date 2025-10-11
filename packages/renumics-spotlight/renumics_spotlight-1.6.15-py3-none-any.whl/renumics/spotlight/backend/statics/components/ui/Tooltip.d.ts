import * as React from 'react';
import Popup from './Popup';
interface Props {
    content?: React.ReactNode;
    visible?: boolean;
    followCursor?: boolean;
    reference?: React.RefObject<Element>;
    borderless?: boolean;
    delay?: number | [number, number];
    duration?: number | [number, number];
    disabled?: boolean;
    children?: React.ReactNode;
    placement?: React.ComponentProps<typeof Popup>['placement'];
}
declare const Tooltip: ({ content, visible, followCursor, reference, borderless, delay, duration, disabled, children, placement, }: Props) => JSX.Element;
export default Tooltip;
