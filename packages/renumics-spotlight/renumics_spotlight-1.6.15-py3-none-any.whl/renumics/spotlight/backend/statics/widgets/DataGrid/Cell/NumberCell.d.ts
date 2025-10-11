import { FunctionComponent } from 'react';
import { NumberColumn } from '../../../types';
interface Props {
    column: NumberColumn;
    value: number;
}
declare const NumberCell: FunctionComponent<Props>;
export default NumberCell;
