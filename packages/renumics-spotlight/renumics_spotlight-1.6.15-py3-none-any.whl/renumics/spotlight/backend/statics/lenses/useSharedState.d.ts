import { Setter } from '../types';
export declare function useSharedState<T = unknown>(key: string, defaultValue: T): [T, Setter<T>];
