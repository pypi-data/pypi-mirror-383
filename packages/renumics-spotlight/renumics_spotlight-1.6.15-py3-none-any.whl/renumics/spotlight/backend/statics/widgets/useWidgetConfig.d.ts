/// <reference types="react" />
type Setter<T> = React.Dispatch<React.SetStateAction<T>>;
type Return<T> = [T, Setter<T>];
declare function useWidgetConfig<T>(name: string): Return<T | undefined>;
declare function useWidgetConfig<T>(name: string, initialState: T): Return<T>;
export default useWidgetConfig;
