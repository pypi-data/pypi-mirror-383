import { ReactNode } from 'react';
interface Props {
    content?: ReactNode;
    tooltip?: ReactNode;
    children?: ReactNode;
    onHide?: () => void;
    onShow?: () => void;
    className?: string;
}
export declare const DropdownContext: import("react").Context<{
    visible: boolean;
    show: () => void;
    hide: () => void;
}>;
declare const Dropdown: ({ content, tooltip, children, onShow, onHide, className, }: Props) => JSX.Element;
export default Dropdown;
