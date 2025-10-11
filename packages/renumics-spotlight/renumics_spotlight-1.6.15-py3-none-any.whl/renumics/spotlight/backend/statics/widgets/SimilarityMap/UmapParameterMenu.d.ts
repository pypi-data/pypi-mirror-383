import { UmapMetric } from '../../services/data';
interface Props {
    umapNNeighbors: number;
    umapMetric: UmapMetric;
    umapMinDist: number;
    onChangeUmapNNeighbors: (value: number) => void;
    onChangeUmapMetric: (value?: UmapMetric) => void;
    onChangeUmapMinDist: (value: number) => void;
}
export declare const UmapSimpleMenu: ({ onChangeUmapNNeighbors, onChangeUmapMinDist, }: Props) => JSX.Element;
export declare const UmapAdvancedMenu: ({ umapNNeighbors, umapMinDist, onChangeUmapNNeighbors, onChangeUmapMinDist, }: Props) => JSX.Element;
export declare const UmapParameterMenu: (props: Props) => JSX.Element;
export {};
