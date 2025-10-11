import { FunctionComponent } from 'react';
import { DataColumn, IndexArray } from '../../../types';
export interface Props {
    columnIndex: number;
    rowIndex: number;
    onDeleteColumn?: () => void;
    onDeleteRow?: () => void;
    onDuplicateRow?: () => void;
    onDoEdit?: (column: DataColumn, rowIndices: IndexArray) => void;
}
declare const CellContextMenu: FunctionComponent<Props>;
export default CellContextMenu;
