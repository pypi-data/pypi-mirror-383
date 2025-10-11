import { FunctionComponent, ReactNode } from 'react';
type Props = {
    isVisible?: boolean;
    title?: string;
    message?: string;
    onAccept?: () => void;
    acceptText?: string;
    onCancel?: () => void;
    cancelText?: string;
    children?: ReactNode;
};
declare const ConfirmationDialog: FunctionComponent<Props>;
export default ConfirmationDialog;
