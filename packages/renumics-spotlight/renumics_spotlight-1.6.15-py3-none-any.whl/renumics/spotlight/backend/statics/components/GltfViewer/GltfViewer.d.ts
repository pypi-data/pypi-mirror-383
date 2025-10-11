import * as React from 'react';
import { Palette } from '../../palettes';
import { MeshAttribute } from './GltfScene';
import { MorphStyle } from './morphing';
export interface ViewerState {
    availableAttributes: MeshAttribute[];
}
export interface Props {
    data?: string | ArrayBuffer;
    color?: string;
    onChange?: (state: ViewerState) => void;
    onLoad?: () => void;
    sync?: boolean;
    syncKey?: string;
    morphStyle?: MorphStyle;
    morphScale?: number;
    colorPalette?: Palette;
    showWireframe?: boolean;
    transparency?: number;
}
export interface Handle {
    reset: () => void;
    fit: () => void;
    makeSyncReference: () => void;
}
declare const _default: React.ForwardRefExoticComponent<Props & React.RefAttributes<Handle>>;
export default _default;
