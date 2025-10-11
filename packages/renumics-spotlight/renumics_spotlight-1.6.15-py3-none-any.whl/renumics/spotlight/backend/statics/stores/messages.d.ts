export interface State {
    persistentErrors: string[];
    addPersistentError: (message: string) => void;
    removePersistentError: (message: string) => void;
    persistentWarnings: string[];
    addPersistentWarning: (message: string) => void;
    removePersistentWarning: (message: string) => void;
}
export declare const useMessages: import("zustand").UseBoundStore<import("zustand").StoreApi<State>>;
