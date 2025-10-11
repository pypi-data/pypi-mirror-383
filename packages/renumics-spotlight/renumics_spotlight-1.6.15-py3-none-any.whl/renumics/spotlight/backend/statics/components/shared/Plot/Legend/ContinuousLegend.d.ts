import { Color } from 'chroma-js';
import { ContinuousTransferFunction } from '../../../../hooks/useColorTransferFunction';
import { Alignment, Arrangement } from './index';
export interface ContinuousProps {
    steps: Color[];
    domain: [number, number];
    arrange?: Arrangement;
    align?: Alignment;
}
export declare const ContinuousLegend: ({ align, arrange, steps, domain, }: ContinuousProps) => JSX.Element;
interface ContinuousTransferFunctionLegendProps extends Omit<ContinuousProps, 'steps' | 'domain'> {
    transferFunction: ContinuousTransferFunction;
}
export declare const ContinuousTransferFunctionLegend: ({ transferFunction, ...props }: ContinuousTransferFunctionLegendProps) => JSX.Element;
export {};
