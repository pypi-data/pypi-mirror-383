import { ReactNode } from 'react';
import { DragData } from './types';
interface Props {
    data: DragData;
    children: ReactNode;
}
export default function Draggable({ data, children }: Props): JSX.Element;
export {};
