import { Color } from 'chroma-js';
import { CategoricalTransferFunction } from '../../../../hooks/useColorTransferFunction';
import * as React from 'react';
import { Alignment, Arrangement } from '.';
export interface CategoricalProps {
    colorMap: {
        label: string;
        color: Color;
    }[];
    align?: Alignment;
    arrange?: Arrangement;
}
export declare const CategoricalLegend: React.FunctionComponent<CategoricalProps>;
interface CategoricalTransferFunctionLegendProps extends Omit<CategoricalProps, 'colorMap'> {
    transferFunction: CategoricalTransferFunction;
}
export declare const CategoricalTransferFunctionLegend: React.FunctionComponent<CategoricalTransferFunctionLegendProps>;
export {};
