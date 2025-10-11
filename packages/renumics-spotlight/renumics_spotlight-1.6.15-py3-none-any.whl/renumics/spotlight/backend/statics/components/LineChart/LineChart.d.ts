import * as React from 'react';
import { Vec2 } from '../../types';
type Domain = [number, number];
export type Series = {
    name: string;
    values: Vec2[];
    xLabel?: string;
    yLabel?: string;
};
export type LineChartProps = {
    chartData: Series[];
    highlightedRegions?: [number, number][];
    multipleYScales?: boolean;
    chartColors?: string[];
    xExtents?: Vec2;
    onChangeXExtents?: (ext: Vec2) => void;
    syncKey?: string;
    yDomains?: Domain[];
};
export interface Handle {
    reset: () => void;
}
declare const _default: React.ForwardRefExoticComponent<LineChartProps & React.RefAttributes<Handle>>;
export default _default;
