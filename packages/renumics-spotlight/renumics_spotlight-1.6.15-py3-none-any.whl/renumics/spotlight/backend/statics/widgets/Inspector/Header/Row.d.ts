import { CSSProperties, FunctionComponent } from 'react';
import type { DraggableProvided } from 'react-beautiful-dnd';
import type { ListChildComponentProps as RowProps } from 'react-window';
declare const RowFactory: FunctionComponent<RowProps>;
type DroppableItemProps = {
    index: number;
    style: CSSProperties;
    provided: DraggableProvided;
    isDropped?: boolean;
};
export declare const DroppableRowItem: FunctionComponent<DroppableItemProps>;
export default RowFactory;
