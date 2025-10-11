import Tippy from '@tippyjs/react';
import * as React from 'react';
import { ComponentProps, FunctionComponent } from 'react';
import type { Placement } from 'tippy.js';
type TippyProps = ComponentProps<typeof Tippy>;
interface Props {
    content?: React.ReactNode;
    visible?: boolean;
    followCursor?: boolean;
    reference?: React.RefObject<Element>;
    delay?: number | [number, number];
    duration?: number | [number, number];
    disabled?: boolean;
    className?: string;
    placement?: Placement;
    interactive?: boolean;
    offset?: [number, number];
    onShow?: TippyProps['onShow'];
    onMount?: TippyProps['onMount'];
    onHide?: TippyProps['onHide'];
    onClickOutside?: TippyProps['onClickOutside'];
    children: React.ReactNode;
}
declare const Popup: FunctionComponent<Props>;
export default Popup;
