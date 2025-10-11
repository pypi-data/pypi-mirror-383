import { MergeStrategy } from './types';
interface Props {
    colors: string[];
    sizes: number[];
    selected: boolean[];
    hidden: boolean[];
    onClick?: (index?: number, mergeMode?: MergeStrategy) => void;
}
declare const Points: ({ colors, sizes, hidden, selected, onClick }: Props) => JSX.Element;
export default Points;
