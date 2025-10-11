export declare const morphStyles: readonly ["loop", "oscillate"];
export type MorphStyle = (typeof morphStyles)[number];
export declare function calculateMorphPosition(at: number, style: MorphStyle): number;
