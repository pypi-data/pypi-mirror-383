export type ErrorHandler = (e?: Error) => void;
export type StateSetter<T> = (value?: T | ((previousValue?: T) => T | undefined)) => void;
export type ReturnType<T> = [T, StateSetter<T>, boolean];
declare function usePersistentState<T>(key: string): ReturnType<T | undefined>;
declare function usePersistentState<T>(key: string, initialValue: T): ReturnType<T>;
export default usePersistentState;
