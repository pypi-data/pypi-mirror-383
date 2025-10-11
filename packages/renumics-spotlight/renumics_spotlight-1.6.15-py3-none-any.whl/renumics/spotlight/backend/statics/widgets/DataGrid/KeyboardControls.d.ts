import { PropsWithChildren } from 'react';
interface Props {
    scrollToRow: (index: number) => void;
}
declare const KeyboardControls: ({ scrollToRow, children, }: PropsWithChildren<Props>) => JSX.Element;
export default KeyboardControls;
