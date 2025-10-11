export declare const notations: readonly ["scientific", "standard"];
export type Notation = (typeof notations)[number];
export interface AppSettings {
    numberNotation: Notation;
    setNumberNotation: (notation: Notation) => void;
}
export declare const useAppSettings: import("zustand").UseBoundStore<Omit<import("zustand").StoreApi<AppSettings>, "persist"> & {
    persist: {
        setOptions: (options: Partial<import("zustand/middleware").PersistOptions<AppSettings, AppSettings>>) => void;
        clearStorage: () => void;
        rehydrate: () => void | Promise<void>;
        hasHydrated: () => boolean;
        onHydrate: (fn: (state: AppSettings) => void) => () => void;
        onFinishHydration: (fn: (state: AppSettings) => void) => () => void;
        getOptions: () => Partial<import("zustand/middleware").PersistOptions<AppSettings, AppSettings>>;
    };
}>;
