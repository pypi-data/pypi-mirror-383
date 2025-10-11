import chroma from 'chroma-js';
interface BBoxProps {
    x: number;
    y: number;
    width: number;
    height: number;
    color: chroma.Color;
    label: string;
}
declare const BBox: ({ x, y, width, height, color, label }: BBoxProps) => JSX.Element;
export default BBox;
