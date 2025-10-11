import chroma from 'chroma-js';
import _ from 'lodash';
export declare const NO_DATA: chroma.Color;
interface BasePalette {
    name: string;
    scale: () => chroma.Scale<chroma.Color>;
    kind: string;
}
export interface CategoricalPalette extends BasePalette {
    maxClasses: number;
    kind: 'categorical';
}
export interface ContinuousPalette extends BasePalette {
    kind: 'continuous';
}
export interface ConstantPalette extends BasePalette {
    kind: 'constant';
}
export type Palette = ContinuousPalette | CategoricalPalette | ConstantPalette;
export declare const constantPalettes: ConstantPalette[];
export declare const constantPalettesByName: _.Dictionary<ConstantPalette>;
export declare const categoricalPalettes: CategoricalPalette[];
export declare const categoricalPalettesByName: _.Dictionary<CategoricalPalette>;
export declare const continuousPalettes: ContinuousPalette[];
export declare const continuousPalettesByName: _.Dictionary<ContinuousPalette>;
export declare const palettes: (CategoricalPalette | ContinuousPalette | ConstantPalette)[];
export declare const defaultConstantPalette: ConstantPalette;
export declare const defaultCategoricalPalette: CategoricalPalette;
export declare const defaultContinuousPalette: ContinuousPalette;
export {};
