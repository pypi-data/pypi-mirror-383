import { FunctionComponent } from 'react';
interface Props {
    min?: number;
    max?: number;
    marks?: {
        [key: number]: string;
    };
    value?: number;
    step?: number;
    showTooltip?: boolean;
    tooltip?: (value: number) => string;
    onChange?: (value: number) => void;
    onRelease?: (value: number) => void;
    disabled?: boolean;
}
declare const Slider: FunctionComponent<Props>;
export default Slider;
