/// <reference types="react" />
interface Props {
    content: (index?: number) => JSX.Element | undefined;
}
declare const Tooltip: ({ content }: Props) => JSX.Element;
export default Tooltip;
