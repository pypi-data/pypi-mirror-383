import { ReactNode } from 'react';
import { DragData } from './types';
interface Props<Data extends DragData> {
    onDrop: (data: Data) => void;
    accepts?: (data: DragData) => boolean;
    children?: ReactNode;
    className?: string;
}
export default function Droppable<Data extends DragData>({ onDrop, accepts, className, children, }: Props<Data>): JSX.Element;
export {};
