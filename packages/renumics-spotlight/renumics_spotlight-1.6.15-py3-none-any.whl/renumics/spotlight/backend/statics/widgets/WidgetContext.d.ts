/// <reference types="react" />
import { Config } from './types';
interface WidgetContextValue {
    widgetId: string;
    config: Config;
    setConfig: React.Dispatch<React.SetStateAction<Config>>;
}
export declare const WidgetContext: import("react").Context<WidgetContextValue>;
export declare const useWidgetContext: () => WidgetContextValue;
export {};
