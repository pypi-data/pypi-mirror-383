import { FunctionComponent } from 'react';
import { CategoricalColumn } from '../../../types';
interface Props {
    column: CategoricalColumn;
    value: number;
}
declare const CategoricalCell: FunctionComponent<Props>;
export default CategoricalCell;
