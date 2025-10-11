import { ReactNode } from 'react';
export interface Props {
    value?: boolean;
    onChange?: (value: boolean) => void;
    children?: ReactNode;
}
declare const Switch: ({ value, onChange, children }: Props) => JSX.Element;
export default Switch;
