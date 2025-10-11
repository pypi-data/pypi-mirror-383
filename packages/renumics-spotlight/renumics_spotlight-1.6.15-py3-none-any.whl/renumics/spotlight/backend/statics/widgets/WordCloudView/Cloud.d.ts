/// <reference types="react" />
import d3Cloud from 'd3-cloud';
export interface Word extends d3Cloud.Word {
    count: number;
    filteredCount: number;
    rowIds: number[];
    text: string;
}
interface Props {
    words: Record<string, Omit<Word, 'text'>>;
    scaling?: 'linear' | 'log' | 'sqrt';
    width: number;
    height: number;
    wordCount?: number;
    hideFiltered?: boolean;
}
export interface Ref {
    reset: () => void;
}
declare const Cloud: import("react").ForwardRefExoticComponent<Props & import("react").RefAttributes<Ref>>;
export default Cloud;
