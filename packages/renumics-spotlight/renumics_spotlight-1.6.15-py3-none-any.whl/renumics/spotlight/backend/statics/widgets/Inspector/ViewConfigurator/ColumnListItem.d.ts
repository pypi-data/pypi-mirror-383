import { DataColumn } from '../../../types';
interface Props {
    column: DataColumn;
    selected: boolean;
    onChangeSelected?: (column: DataColumn, selected: boolean) => void;
    className?: string;
}
declare const ColumnListItem: ({ column, selected, onChangeSelected, className, }: Props) => JSX.Element;
export default ColumnListItem;
