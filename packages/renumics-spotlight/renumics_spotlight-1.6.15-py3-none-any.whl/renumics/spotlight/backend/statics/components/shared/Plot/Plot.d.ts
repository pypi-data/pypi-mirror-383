/// <reference types="react" />
import { Point2d } from './types';
interface Props {
    points: Point2d[];
    scaleUniform?: boolean;
    children: JSX.Element[] | JSX.Element;
    isPointHighlighted: (index: number) => boolean;
    setHighlightedPoint: (index: number | undefined) => void;
}
declare const Plot: ({ points, isPointHighlighted, setHighlightedPoint, scaleUniform, children, }: Props) => JSX.Element;
export default Plot;
