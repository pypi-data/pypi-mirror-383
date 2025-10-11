interface MelScale {
    (value: number): number;
    toMelScale(value: number): number;
    fromMelScale(frequency: number): number;
    domain(): number[];
    domain(domain: number[]): MelScale;
    range(): number[];
    range(range: number[]): MelScale;
    copy(): MelScale;
    invert(value: number): number;
    ticks(count?: number): number[];
    tickFormat(count?: number, specifier?: string): (d: number) => string;
}
declare const melScale: () => MelScale;
export default melScale;
