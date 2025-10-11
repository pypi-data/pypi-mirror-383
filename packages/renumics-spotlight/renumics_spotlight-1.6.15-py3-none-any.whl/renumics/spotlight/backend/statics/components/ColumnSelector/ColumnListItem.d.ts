import { DataColumn } from '../../types';
interface Props {
    column: DataColumn;
    selected: boolean;
    onChangeSelected?: (column: DataColumn, selected: boolean) => void;
}
declare const ColumnListItem: ({ column, selected, onChangeSelected }: Props) => JSX.Element;
export default ColumnListItem;
