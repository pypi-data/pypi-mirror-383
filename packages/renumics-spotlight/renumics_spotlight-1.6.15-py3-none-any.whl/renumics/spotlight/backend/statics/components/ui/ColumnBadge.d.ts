import { type CSSProp } from 'styled-components';
interface Props {
    columnKey: string;
    draggable?: boolean;
    className?: string;
    css?: CSSProp;
}
declare const ColumnBadge: ({ columnKey, className, draggable, }: Props) => JSX.Element;
export default ColumnBadge;
