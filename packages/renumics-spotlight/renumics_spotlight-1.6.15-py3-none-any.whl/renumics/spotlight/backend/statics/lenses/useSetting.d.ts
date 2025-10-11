import { Setter } from '../types';
declare function useSetting<T>(name: string, defaultValue: T): [T, Setter<T>];
export default useSetting;
