import { FunctionComponent } from 'react';
import { DataColumn, TableData } from '../../types';
export interface Props {
    rowIndex: number;
    data: TableData;
    placementColumns: DataColumn[];
    colorColumn?: DataColumn;
    scaleColumn?: DataColumn;
    interestingColumns?: DataColumn[];
    filter: boolean;
}
declare const TooltipContent: FunctionComponent<Props>;
export default TooltipContent;
