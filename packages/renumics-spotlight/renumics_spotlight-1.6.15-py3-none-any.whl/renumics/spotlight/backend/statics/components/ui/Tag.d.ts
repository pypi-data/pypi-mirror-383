import { Color } from 'chroma-js';
interface Props {
    tag: string;
    color?: Color;
    className?: string;
}
declare const Tag: ({ tag, color, className, }: Props) => JSX.Element;
export default Tag;
