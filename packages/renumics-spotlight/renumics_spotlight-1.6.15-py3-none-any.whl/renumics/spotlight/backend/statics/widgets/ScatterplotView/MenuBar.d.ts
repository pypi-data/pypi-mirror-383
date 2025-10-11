/// <reference types="react" />
interface MenuProps {
    placeableColumns: string[];
    colorableColumns: string[];
    scaleableColumns: string[];
    xAxisColumn?: string;
    yAxisColumn?: string;
    colorBy?: string;
    sizeBy?: string;
    filter: boolean;
    onChangeXAxisColumn: (column: string) => void;
    onChangeYAxisColumn: (column: string) => void;
    onChangeColorBy: (column: string) => void;
    onChangeSizeBy: (column: string) => void;
    onChangeFilter: (filter: boolean) => void;
    onReset: () => void;
}
declare const _default: import("react").NamedExoticComponent<MenuProps>;
export default _default;
