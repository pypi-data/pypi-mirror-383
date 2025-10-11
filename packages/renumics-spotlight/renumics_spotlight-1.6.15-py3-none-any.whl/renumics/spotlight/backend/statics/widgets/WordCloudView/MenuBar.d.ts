import { ComponentProps } from 'react';
import Cloud from './Cloud';
export type BoolOpeartion = 'difference' | 'intersection' | 'union' | 'symmetric difference';
interface MenuProps {
    placeableColumns: string[];
    wordCloudBy?: string;
    filter: boolean;
    scaling: ComponentProps<typeof Cloud>['scaling'];
    onChangeScaling: (scaling: ComponentProps<typeof Cloud>['scaling']) => void;
    onChangeWordCloudColumn: (column?: string) => void;
    onChangeFilter: (filter: boolean) => void;
    onReset: () => void;
    maxWordCount: number;
    minWordCount: number;
    minWordLength: number;
    maxWordLength: number;
    onChangeMinWordLength: (value: number) => void;
    wordCount: number;
    onChangeWordCount: (value: number) => void;
    stopwords: string[];
    onChangeStopwords: (values: string[]) => void;
}
declare const _default: import("react").NamedExoticComponent<MenuProps>;
export default _default;
