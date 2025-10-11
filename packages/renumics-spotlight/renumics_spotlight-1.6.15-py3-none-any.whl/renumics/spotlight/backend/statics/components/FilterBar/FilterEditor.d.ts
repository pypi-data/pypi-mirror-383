import { FunctionComponent } from 'react';
import { Filter } from '../../types';
interface Props {
    filter?: Filter;
    onAccept: (filter: Filter) => void;
    onCancel: () => void;
}
declare const FilterEditor: FunctionComponent<Props>;
export default FilterEditor;
