import { MergeStrategy } from './types';
interface Props {
    hidden: boolean[];
    onSelect: (key: number[], mergeStrategy: MergeStrategy) => void;
}
declare const Brush: ({ hidden, onSelect }: Props) => JSX.Element;
export default Brush;
