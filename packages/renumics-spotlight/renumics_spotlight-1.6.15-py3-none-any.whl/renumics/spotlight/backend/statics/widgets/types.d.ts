import { FunctionComponent } from 'react';
export type Config = Record<string, unknown>;
export interface WidgetProps {
    widgetId: string;
}
interface WidgetAttributes {
    defaultName: string;
    icon: (props?: any) => JSX.Element;
    key: string;
    legacyKeys?: string[];
}
export type Widget<P = {}> = FunctionComponent<P & WidgetProps> & WidgetAttributes;
export {};
