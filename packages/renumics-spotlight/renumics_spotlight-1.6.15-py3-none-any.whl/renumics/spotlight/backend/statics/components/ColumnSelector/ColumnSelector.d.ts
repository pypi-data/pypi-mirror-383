import { DataColumn } from '../../types';
interface Props {
    availableColumns: DataColumn[];
    columns: DataColumn[];
    onChange?: (columns: DataColumn[]) => void;
}
declare const ColumnSelector: ({ availableColumns, columns, onChange, }: Props) => JSX.Element;
export default ColumnSelector;
