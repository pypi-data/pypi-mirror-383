import { DataKind } from './datatypes';
import { Predicate } from './types';
export declare const getApplicablePredicates: (kind: DataKind) => Record<string, Predicate>;
export declare const hasApplicablePredicates: (kind: DataKind) => boolean;
