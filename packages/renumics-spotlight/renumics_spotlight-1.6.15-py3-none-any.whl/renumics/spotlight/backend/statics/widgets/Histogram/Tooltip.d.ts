import { TransferFunction } from '../../hooks/useColorTransferFunction';
import { ReactNode } from 'react';
import { BinKey, HistogramData } from './types';
interface Props {
    xKey?: BinKey;
    yKey?: BinKey;
    histogramm: HistogramData;
    children?: ReactNode;
    transferFunction: TransferFunction;
}
declare const Tooltip: ({ xKey, yKey, histogramm, children, transferFunction, }: Props) => JSX.Element;
export default Tooltip;
