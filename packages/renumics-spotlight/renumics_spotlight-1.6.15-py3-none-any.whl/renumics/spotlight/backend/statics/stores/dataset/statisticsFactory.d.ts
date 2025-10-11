import { DataType } from '../../datatypes';
import { ColumnData, ColumnsStats, DataColumn, DataStatistics } from '../../types';
export declare const makeStats: (type: DataType, data: ColumnData, mask?: boolean[]) => DataStatistics | undefined;
export declare const makeColumnsStats: (columns: DataColumn[], data: Record<string, ColumnData>, mask?: boolean[]) => ColumnsStats;
