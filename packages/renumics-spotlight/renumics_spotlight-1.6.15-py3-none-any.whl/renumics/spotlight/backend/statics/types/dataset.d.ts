import * as datatypes from '../datatypes';
import { IndexArray } from './base';
export interface DataColumn {
    index: number;
    key: string;
    name: string;
    type: datatypes.DataType;
    editable: boolean;
    optional: boolean;
    computed: boolean;
    hidden: boolean;
    description: string;
    tags: string[];
}
export interface NumberColumn extends DataColumn {
    type: datatypes.NumericalDataType;
}
export declare const isNumberColumn: (col: DataColumn) => col is NumberColumn;
export interface StringColumn extends DataColumn {
    type: datatypes.StringDataType;
}
export declare const isStringColumn: (col: DataColumn) => col is StringColumn;
export interface BooleanColumn extends DataColumn {
    type: datatypes.BooleanDataType;
}
export declare const isBooleanColumn: (col: DataColumn) => col is BooleanColumn;
export interface CategoricalColumn extends DataColumn {
    type: datatypes.CategoricalDataType;
}
export declare const isCategoricalColumn: (col: DataColumn) => col is CategoricalColumn;
export interface ScalarColumn extends DataColumn {
    type: datatypes.ScalarDataType;
}
export declare const isScalarColumn: (col: DataColumn) => col is ScalarColumn;
export interface ArrayColumn extends DataColumn {
    type: datatypes.ScalarDataType;
}
export declare const isArrayColumn: (col: DataColumn) => col is ArrayColumn;
export interface EmbeddingColumn extends DataColumn {
    type: datatypes.EmbeddingDataType;
}
export declare const isEmbeddingColumn: (col: DataColumn) => col is EmbeddingColumn;
export interface DateColumn extends DataColumn {
    type: datatypes.DateTimeDataType;
}
export declare const isDateColumn: (col: DataColumn) => col is DateColumn;
export interface Sequence1DColumn extends DataColumn {
    type: datatypes.Sequence1DDataType;
    yLabel?: string;
    xLabel?: string;
}
export declare const isSequence1DColumn: (col: DataColumn) => col is Sequence1DColumn;
export interface MeshColumn extends DataColumn {
    type: datatypes.MeshDataType;
}
export declare const isMeshColumn: (col: DataColumn) => col is MeshColumn;
export interface ImageColumn extends DataColumn {
    type: datatypes.ImageDataType;
}
export declare const isImageColumn: (col: DataColumn) => col is ImageColumn;
export interface UnknownColumn extends DataColumn {
    type: datatypes.UnknownDataType;
}
export declare const isUnknownColumn: (col: DataColumn) => col is UnknownColumn;
export interface RowValues {
    [key: string]: any;
}
export interface DataRow {
    index: number;
    values: RowValues;
}
export type ColumnData = any[] | Int32Array | Float32Array;
export type TableData = Record<string, ColumnData>;
export interface DataStatistics {
    max: number;
    min: number;
    mean: number;
    p95: number;
    p5: number;
    std: number;
}
export type ColumnsStats = Record<string, DataStatistics | undefined>;
export interface DataFrame {
    columns: DataColumn[];
    length: number;
    data: TableData;
}
export type TableView = 'full' | 'filtered' | 'selected';
export interface DataIssue {
    severity: 'low' | 'medium' | 'high';
    title: string;
    rows: IndexArray;
    columns?: DataColumn[];
    description?: string;
}
