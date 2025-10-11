import * as datatypes from '../datatypes';
import type { DataColumn, TableData } from './dataset';
export interface Predicate<T = any> {
    shorthand: string;
    compare: (value: any, referenceValue: T) => boolean;
}
export declare abstract class Filter {
    kind: string;
    isEnabled: boolean;
    isInverted: boolean;
    abstract apply(rowIndex: number, data: TableData): boolean;
}
export declare class PredicateFilter<T = any> extends Filter {
    kind: 'PredicateFilter';
    column: DataColumn;
    predicate: Predicate<T>;
    referenceValue: T;
    constructor(column: DataColumn, predicate: Predicate<T>, referenceValue: T);
    get type(): datatypes.DataType;
    apply(rowIndex: number, data: TableData): boolean;
}
export declare class SetFilter extends Filter {
    kind: 'SetFilter';
    rowIndices: Set<number>;
    name: string;
    constructor(rows: number[] | Set<number>, name?: string);
    static fromMask(mask: boolean[], name?: string): SetFilter;
    apply(rowIndex: number): boolean;
}
