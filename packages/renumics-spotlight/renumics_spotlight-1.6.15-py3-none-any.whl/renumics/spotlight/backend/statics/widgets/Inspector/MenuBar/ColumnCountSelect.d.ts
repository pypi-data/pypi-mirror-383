import { FunctionComponent } from 'react';
interface Props {
    visibleColumnsCount: number;
    setVisibleColumnsCount: (count: number) => void;
    visibleColumnsCountOptions: number[];
}
declare const ColumnCountSelect: FunctionComponent<Props>;
export default ColumnCountSelect;
