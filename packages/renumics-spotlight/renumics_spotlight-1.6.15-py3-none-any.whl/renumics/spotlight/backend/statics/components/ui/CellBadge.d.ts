import { type CSSProp } from 'styled-components';
interface Props {
    columnKey: string;
    row: number;
    draggable?: boolean;
    className?: string;
    css?: CSSProp;
}
declare const CellBadge: ({ columnKey, row, className, draggable, }: Props) => JSX.Element;
export default CellBadge;
