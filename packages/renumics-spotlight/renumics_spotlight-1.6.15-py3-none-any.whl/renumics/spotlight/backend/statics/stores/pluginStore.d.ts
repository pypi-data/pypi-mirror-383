/// <reference types="react" />
import { Widget } from '../widgets/types';
import { Lens } from '../types';
export interface App {
    registerWidget: (widget: Widget) => void;
    registerLens: (lens: Lens) => void;
    addAppBarItem: (component: JSX.Element) => void;
    removeAppBarItemByKey: (key: string) => void;
}
interface PluginModule {
    activate?: (app: App) => void;
}
interface Plugin {
    name: string;
    priority: number;
    module?: PluginModule;
}
interface State {
    plugins?: Plugin[];
    init: () => void;
}
declare const usePluginStore: import("zustand").UseBoundStore<import("zustand").StoreApi<State>>;
export default usePluginStore;
