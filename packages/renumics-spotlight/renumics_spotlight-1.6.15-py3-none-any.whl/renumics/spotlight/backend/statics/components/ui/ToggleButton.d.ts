import { FunctionComponent } from 'react';
import { Props as ButtonProps } from './Button';
type Props = {
    checked?: boolean;
    onChange?: ({ checked }: {
        checked: boolean;
    }) => void;
    tooltip?: string;
} & ButtonProps;
declare const ToggleButton: FunctionComponent<Props>;
export default ToggleButton;
