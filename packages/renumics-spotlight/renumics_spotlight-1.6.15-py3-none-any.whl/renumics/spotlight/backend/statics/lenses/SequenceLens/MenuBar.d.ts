import { FunctionComponent } from 'react';
interface Props {
    groupY: boolean;
    isXSynchronized: boolean;
    isYSynchronized: boolean;
    onChangeGroupY: (show: boolean) => void;
    onReset: () => void;
    onChangeIsXSynchronized: (isSynchronized: boolean) => void;
    onChangeIsYSynchronized: (isSynchronized: boolean) => void;
}
declare const MenuBar: FunctionComponent<Props>;
export default MenuBar;
