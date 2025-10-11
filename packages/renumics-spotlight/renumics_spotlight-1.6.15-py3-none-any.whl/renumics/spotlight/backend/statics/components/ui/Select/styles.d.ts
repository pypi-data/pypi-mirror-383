import type { StylesConfig } from 'react-select';
import { OptionType, SelectVariant, Value } from './types';
export declare function makeStyles<T extends Value, M extends boolean = false>(variant?: SelectVariant): StylesConfig<OptionType<T>, M>;
