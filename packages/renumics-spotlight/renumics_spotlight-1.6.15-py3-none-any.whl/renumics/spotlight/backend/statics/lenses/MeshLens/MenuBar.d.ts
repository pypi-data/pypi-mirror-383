import { MorphStyle } from '../../components//GltfViewer';
import { FunctionComponent } from 'react';
interface Props {
    isViewSynced: boolean;
    availableColors: string[];
    availableMorphStyles: readonly MorphStyle[];
    morphStyle: MorphStyle;
    morphScale: number;
    transparency: number;
    colorAttributeName: string;
    showWireframe: boolean;
    onChangeShowWireframe: (enabled: boolean) => void;
    onReset: () => void;
    onFit: () => void;
    onToggleSync: (enabled: boolean) => void;
    onChangeColorAttributeName: (color: string) => void;
    onChangeMorphStyle: (morphStyle: MorphStyle) => void;
    onChangeMorphScale: (value: number) => void;
    onChangeTransparency: (value: number) => void;
}
declare const MenuBar: FunctionComponent<Props>;
export default MenuBar;
