/**
 * Omit large amount of tailing zeros.
 */
declare const freqType: (x: number) => number;
/**
 * Get appropriate SI suffix for frequency.
 */
declare const unitType: (x: number) => "MHz" | "KHz" | "Hz";
/**
 * Set window to edges to start/end of track if NaN.
 * Swap window values if start > end.
 */
declare const fixWindow: (window: [
    number,
    number
] | undefined, duration: number) => [number, number];
declare const amplitudeToDb: (amplitude: number, ref: number, amin: number) => number;
declare const hzToMel: (freq: number) => number;
declare const melToHz: (mel: number) => number;
export { unitType, freqType, fixWindow, amplitudeToDb, hzToMel, melToHz };
