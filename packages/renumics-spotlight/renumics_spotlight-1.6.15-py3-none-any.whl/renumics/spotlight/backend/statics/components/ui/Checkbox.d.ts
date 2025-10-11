import { FunctionComponent } from 'react';
interface Props {
    onChange?: (checked: boolean) => void;
    checked: boolean;
    className?: string;
}
declare const Checkbox: FunctionComponent<Props>;
export default Checkbox;
