import { CategoricalPalette, ConstantPalette, ContinuousPalette } from '../palettes';
export interface ColorsState {
    constantPalette: ConstantPalette;
    categoricalPalette: CategoricalPalette;
    continuousPalette: ContinuousPalette;
    robust: boolean;
    continuousInts: boolean;
    continuousCategories: boolean;
    setConstantPalette: (palette?: ConstantPalette) => void;
    setCategoricalPalette: (palette?: CategoricalPalette) => void;
    setContinuousPalette: (palette?: ContinuousPalette) => void;
    setRobust: (robust: boolean) => void;
    setContinuousInts: (continuous: boolean) => void;
    setContinuousCategories: (continuous: boolean) => void;
}
export declare const useColors: import("zustand").UseBoundStore<Omit<import("zustand").StoreApi<ColorsState>, "persist"> & {
    persist: {
        setOptions: (options: Partial<import("zustand/middleware").PersistOptions<ColorsState, any>>) => void;
        clearStorage: () => void;
        rehydrate: () => void | Promise<void>;
        hasHydrated: () => boolean;
        onHydrate: (fn: (state: ColorsState) => void) => () => void;
        onFinishHydration: (fn: (state: ColorsState) => void) => () => void;
        getOptions: () => Partial<import("zustand/middleware").PersistOptions<ColorsState, any>>;
    };
}>;
