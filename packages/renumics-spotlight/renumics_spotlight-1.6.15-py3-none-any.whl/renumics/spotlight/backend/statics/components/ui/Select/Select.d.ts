import { PropsWithChildren, ReactElement } from 'react';
import { SelectVariant, Value } from './types';
interface SelectProps<T extends Value> {
    options: readonly T[];
    value?: T;
    defaultValue?: T;
    placeholder?: string;
    variant?: SelectVariant;
    onChange?: (value?: T) => void;
    autoFocus?: boolean;
    openMenuOnFocus?: boolean;
    isDisabled?: boolean;
    label?: (value?: T) => string;
    isSearchable?: boolean;
    isClearable?: boolean;
    canCreate?: boolean;
    singleValueTemplate?: (value: React.ReactNode) => React.ReactNode;
}
declare function Select<T extends Value>({ options, value, defaultValue, placeholder, variant, onChange, autoFocus, openMenuOnFocus, isDisabled, label, singleValueTemplate, canCreate, isSearchable, isClearable, }: PropsWithChildren<SelectProps<T>>): ReactElement;
export default Select;
