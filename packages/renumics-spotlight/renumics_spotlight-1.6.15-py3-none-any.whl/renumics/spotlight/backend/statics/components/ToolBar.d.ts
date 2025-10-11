import { FunctionComponent } from 'react';
interface Props {
    resetWorkspace: () => void;
    saveLayout: () => void;
    loadLayout: (file: File) => void;
}
declare const ToolBar: FunctionComponent<Props>;
export default ToolBar;
