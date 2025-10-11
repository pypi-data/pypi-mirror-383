import { FunctionComponent } from 'react';
interface Props {
    className?: string;
    availableFreqScales: string[];
    availableAmpScales: string[];
    freqScale: string;
    ampScale: string;
    onChangeFreqScale: (scale: string) => void;
    onChangeAmpScale: (scale: string) => void;
}
declare const MenuBar: FunctionComponent<Props>;
export default MenuBar;
