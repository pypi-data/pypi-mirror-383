import * as React from 'react';
import { Config } from './types';
interface Props {
    widgetType: string;
    widgetId: string;
    config: Record<string, unknown>;
    setConfig: React.Dispatch<React.SetStateAction<Config>>;
}
declare const _default: React.MemoExoticComponent<({ widgetType, widgetId, config, setConfig, }: Props) => JSX.Element>;
export default _default;
