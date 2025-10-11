import { ReactNode } from 'react';
type Props = {
    onClickOutside?: () => void;
    isVisible?: boolean;
    children: ReactNode;
    title?: string;
};
declare const Dialog: ({ isVisible, children, onClickOutside, }: Props) => JSX.Element;
export default Dialog;
