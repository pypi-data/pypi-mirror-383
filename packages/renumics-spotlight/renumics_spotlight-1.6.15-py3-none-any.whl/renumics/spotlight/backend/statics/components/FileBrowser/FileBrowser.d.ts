interface Props {
    extensions?: string[];
    cancellable?: boolean;
    openCaption?: string;
    onSelect?: (path?: string) => void;
    onOpen?: (path: string) => void;
    onCancel?: () => void;
}
declare const FileBrowser: ({ onSelect, onOpen, onCancel, openCaption, extensions, cancellable, }: Props) => JSX.Element;
export default FileBrowser;
