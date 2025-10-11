import { ReactNode } from 'react';
import { StoreApi } from 'zustand';
import { LensConfig } from './types';
export interface State {
    lenses: LensConfig[];
    addLens: (view: LensConfig) => void;
    removeLens: (view: LensConfig) => void;
    moveLens: (source: number, target: number) => void;
    changeLens: (key: string, lens: LensConfig | ((prev: LensConfig) => LensConfig)) => void;
}
export declare const StoreContext: import("react").Context<StoreApi<State> | null>;
interface ProviderProps {
    children?: ReactNode;
}
declare const StoreProvider: ({ children }: ProviderProps) => JSX.Element;
declare function useStore<T>(selector: (state: State) => T): T;
export { useStore, StoreProvider };
