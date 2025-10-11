import { TransferFunction } from '../../../../hooks/useColorTransferFunction';
import * as React from 'react';
export type Alignment = 'left' | 'center' | 'right';
export type Arrangement = 'horizontal' | 'vertical';
export declare const DEFAULT_ALIGNMENT = "left";
export declare const DEFAULT_ARRANGEMENT = "horizontal";
interface BaseProps {
    transferFunction: TransferFunction;
    caption: string;
    arrange?: Arrangement;
    className?: string;
    align?: Alignment;
}
export interface ConstantProps {
    kind: 'constant';
}
declare const _default: React.NamedExoticComponent<BaseProps>;
export default _default;
