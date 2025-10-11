import { RefObject } from 'react';
import { VariableSizeGrid as Grid } from 'react-window';
declare function useHighlight(grid: RefObject<Grid>): () => void;
export default useHighlight;
