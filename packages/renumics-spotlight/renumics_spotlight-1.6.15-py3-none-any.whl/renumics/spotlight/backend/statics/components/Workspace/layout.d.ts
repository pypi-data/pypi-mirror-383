import type { IJsonModel } from 'flexlayout-react';
import type { IJsonRowNode } from 'flexlayout-react/declarations/model/IJsonModel';
import { AppLayout, SplitNode } from '../../types';
type Orientation = 'horizontal' | 'vertical';
export declare function convertAppLayoutToFlexLayout(appLayout: AppLayout): IJsonModel['layout'];
export declare function convertFlexRow(node: IJsonRowNode, parentOrientation: Orientation): SplitNode;
export declare function convertFlexLayoutToAppLayout(flexLayout: IJsonModel['layout']): AppLayout;
export {};
