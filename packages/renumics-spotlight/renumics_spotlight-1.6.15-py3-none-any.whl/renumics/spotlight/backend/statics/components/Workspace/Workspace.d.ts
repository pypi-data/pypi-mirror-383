/// <reference types="react" />
export interface Handle {
    reset: () => void;
    loadLayout: (file: File) => void;
    saveLayout: () => void;
}
declare const _default: import("react").ForwardRefExoticComponent<import("react").RefAttributes<Handle>>;
export default _default;
