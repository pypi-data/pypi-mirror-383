import { Palette } from '../../palettes';
export interface Props<T extends Palette> {
    applicableColorPalettes: T[];
    colorPalette?: T;
    onChangeColorPalette?: (palette: T | undefined) => void;
}
declare const ColorPaletteSelect: <T extends Palette>({ applicableColorPalettes, colorPalette, onChangeColorPalette, }: Props<T>) => JSX.Element;
export default ColorPaletteSelect;
