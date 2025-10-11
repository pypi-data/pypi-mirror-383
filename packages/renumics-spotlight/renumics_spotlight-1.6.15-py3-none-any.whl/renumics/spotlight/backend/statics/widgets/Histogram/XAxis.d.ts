import { HistogramData } from './types';
interface FactoryProps {
    width: number;
    height: number;
    histogram: HistogramData;
    hideUnfiltered: boolean;
}
declare const XAxis: (props: FactoryProps) => JSX.Element;
export default XAxis;
