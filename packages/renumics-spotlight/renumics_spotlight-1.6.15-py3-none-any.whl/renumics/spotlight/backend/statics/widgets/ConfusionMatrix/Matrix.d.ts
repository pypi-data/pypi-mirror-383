import type { Cell, MatrixData } from './types';
interface Props {
    data: MatrixData;
    onHoverCell?: (cell?: Cell) => void;
    onClickCell?: (cell?: Cell) => void;
}
declare const Matrix: ({ data, onHoverCell, onClickCell }: Props) => JSX.Element;
export default Matrix;
