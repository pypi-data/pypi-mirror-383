import { DataKind, DataType } from '../datatypes';
import { ColumnData, DataColumn, IndexArray } from '../types';
import { Notation } from '../stores/appSettings';
interface FormatterOptions {
    notation: Notation;
}
export declare class Formatter {
    notation: Notation;
    constructor(options: FormatterOptions);
    canFormat(type: DataType): boolean;
    format(value: any, type: DataType, full?: boolean): string;
    formatFloat(value: number, full?: boolean): string;
}
export declare function useDataformat(): Formatter;
export declare function parse(text: string, type: DataType): number | string | boolean | null | undefined;
type TransferFunction = (val?: number) => number;
export declare const createSizeTransferFunction: (sizeBy: DataColumn | undefined, data: ColumnData, rowIndices: IndexArray) => TransferFunction;
export declare function formatKind(kind: DataKind, plural?: boolean): string;
export declare function formatType(type: DataType, plural?: boolean): string;
export {};
