import { DataType } from '../../datatypes';
import { ReactElement } from 'react';
import * as THREE from 'three';
import { Palette } from '../../palettes';
import { MorphStyle } from './morphing';
export interface MeshAttribute {
    name: string;
    type: DataType;
}
export interface Props {
    data: string | ArrayBuffer;
    colorAttributeName?: string;
    morphStyle: MorphStyle;
    morphScale: number;
    transparency?: number;
    colorPalette?: Palette;
    showWireframe?: boolean;
    onLoad?: (scene: THREE.Group, attributes: MeshAttribute[]) => void;
}
declare const GltfScene: ({ data, colorAttributeName, morphStyle, morphScale, transparency, colorPalette, showWireframe, onLoad, }: Props) => ReactElement;
export default GltfScene;
