interface ReturnType {
    isHighlighted: boolean;
    highlightRow: () => void;
    dehighlightRow: () => void;
}
declare function useRowHighlight(rowIndex: number): ReturnType;
export default useRowHighlight;
