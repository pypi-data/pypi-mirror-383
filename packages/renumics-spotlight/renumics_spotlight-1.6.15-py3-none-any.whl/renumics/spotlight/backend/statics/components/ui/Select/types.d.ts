export type Value = string | number | boolean | object | null;
export type OptionType<T extends Value> = {
    value: T;
};
export type SelectVariant = 'normal' | 'compact' | 'inline' | 'inset';
