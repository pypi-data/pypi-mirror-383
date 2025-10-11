import { TransferFunction } from '../../hooks/useColorTransferFunction';
import { BinKey, HistogramData } from './types';
interface Props {
    width: number;
    height: number;
    histogram: HistogramData;
    hideUnfiltered: boolean;
    transferFunction: TransferFunction;
    onHoverBin: (kwargs?: {
        xKey?: BinKey;
        yKey?: BinKey;
    }) => void;
}
declare const Bars: ({ width, height, histogram, transferFunction, hideUnfiltered, onHoverBin, }: Props) => JSX.Element;
export default Bars;
