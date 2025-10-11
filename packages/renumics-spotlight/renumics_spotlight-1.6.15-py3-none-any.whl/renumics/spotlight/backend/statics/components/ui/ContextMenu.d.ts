import { useSingleton } from '@tippyjs/react';
import type { TippyProps } from '@tippyjs/react';
import * as React from 'react';
import { FunctionComponent } from 'react';
type ContextMenuContextState = {
    _target?: ReturnType<typeof useSingleton>[1];
    _mountedRef: EventTarget | null;
    hide: () => void;
    show: () => void;
};
export declare const ContextMenuProvider: FunctionComponent<{
    children: React.ReactNode;
}>;
declare const ContextMenu: FunctionComponent<Pick<TippyProps, 'content' | 'children'>>;
export declare const useContextMenu: () => Omit<ContextMenuContextState, '_mountedRef' | '_target'>;
export default ContextMenu;
