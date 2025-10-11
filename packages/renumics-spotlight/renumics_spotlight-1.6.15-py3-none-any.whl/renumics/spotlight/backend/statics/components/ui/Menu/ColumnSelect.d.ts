/// <reference types="react" />
import { SelectVariant } from '../Select/types';
export interface Props {
    title?: string;
    selected?: string;
    selectableColumns: string[];
    onChangeColumn: (keys: string) => void;
    variant?: SelectVariant;
}
declare const _default: import("react").NamedExoticComponent<Props>;
export default _default;
