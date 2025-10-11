import type { Widget } from '../widgets/types';
import type { Lens } from '../types';
import { DataType } from '../datatypes';
export declare function isLensCompatible<T>(view: Lens<T>, types: DataType[], canEdit: boolean): boolean;
export interface State {
    widgetsByKey: Record<string, Widget>;
    widgetKeys: string[];
    widgets: Widget[];
    lensesByKey: Record<string, Lens>;
    lensKeys: string[];
    lenses: Lens[];
}
export declare const useComponentsStore: import("zustand").UseBoundStore<import("zustand").StoreApi<State>>;
export declare function findCompatibleLenses(types: DataType[], canEdit: boolean): string[];
export declare function registerWidget(widget: Widget): void;
export declare function registerLens(lens: Lens<any>): void;
