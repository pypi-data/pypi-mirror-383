import { AppLayout } from '../types';
export interface State {
    layout: AppLayout;
    fetch: () => void;
    reset: () => void;
    save: (layout: AppLayout) => void;
    load: (file: File) => void;
}
export declare const useLayout: import("zustand").UseBoundStore<import("zustand").StoreApi<State>>;
