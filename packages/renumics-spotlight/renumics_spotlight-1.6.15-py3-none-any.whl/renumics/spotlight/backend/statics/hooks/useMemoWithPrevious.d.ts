declare function useMemoWithPrevious<T>(callback: (previous: T) => T, dependencies: unknown[], defaultValue: T): T;
export default useMemoWithPrevious;
