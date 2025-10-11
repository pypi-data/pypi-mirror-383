import { FunctionComponent } from 'react';
interface Props {
    visibleColumnsCount: number;
    setVisibleColumnsCount: (count: number) => void;
    visibleColumnsCountOptions: number[];
}
declare const MenuBar: FunctionComponent<Props>;
export default MenuBar;
