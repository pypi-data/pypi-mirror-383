import * as React from 'react';
import * as THREE from 'three';
export interface Props {
    target?: THREE.Vector3;
    sync?: boolean;
    syncKey?: string;
}
interface ExtraMethods {
    reset: (fitTo?: THREE.Object3D) => void;
    fit: (object: THREE.Object3D, offset?: number) => void;
    makeSyncReference: () => void;
}
export type Handle = ExtraMethods;
declare const _default: React.ForwardRefExoticComponent<Props & React.RefAttributes<ExtraMethods>>;
export default _default;
