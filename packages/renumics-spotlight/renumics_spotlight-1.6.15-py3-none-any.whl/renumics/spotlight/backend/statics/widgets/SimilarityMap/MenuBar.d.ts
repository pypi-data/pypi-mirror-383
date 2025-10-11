/// <reference types="react" />
import { Hint } from '../../components/ui/Menu/MultiColumnSelect';
import { PCANormalization, UmapMetric } from '../../services/data';
import { ReductionMethod } from './types';
interface Props {
    colorBy?: string;
    sizeBy?: string;
    placeBy: string[];
    filter: boolean;
    embeddableColumns: string[];
    embeddableColumnsHints?: {
        [key: string]: Hint;
    };
    reductionMethod: ReductionMethod;
    umapNNeighbors: number;
    umapMetric: UmapMetric;
    umapMinDist: number;
    pcaNormalization: PCANormalization;
    onChangeColorBy: (columnName?: string) => void;
    onChangeSizeBy: (columnName?: string) => void;
    onChangePlaceBy: (columnNames: string[]) => void;
    onChangeFilter: (value: boolean) => void;
    onChangeReductionMethod: (value?: ReductionMethod) => void;
    onChangeUmapNNeighbors: (value: number) => void;
    onChangeUmapMetric: (value?: UmapMetric) => void;
    onChangeUmapMinDist: (value: number) => void;
    onChangePCANormalization: (value?: PCANormalization) => void;
    onReset: () => void;
}
declare const _default: import("react").NamedExoticComponent<Props>;
export default _default;
