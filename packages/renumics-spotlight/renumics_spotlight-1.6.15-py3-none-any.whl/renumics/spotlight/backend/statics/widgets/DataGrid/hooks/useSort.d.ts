declare function useSort(): {
    sortedIndices: Int32Array;
    getOriginalIndex: (sortedIndex: number) => number;
    getSortedIndex: (originalIndex: number) => number;
};
export default useSort;
