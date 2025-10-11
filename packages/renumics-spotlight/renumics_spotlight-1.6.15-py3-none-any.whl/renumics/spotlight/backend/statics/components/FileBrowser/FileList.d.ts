import { FileEntry } from '../../client/models/FileEntry';
import { Folder } from '../../client/models/Folder';
interface Props {
    setPath: (path: string) => void;
    folder?: Folder;
    extensions?: string[];
    onOpen?: (path: string) => void;
    selectedFile?: FileEntry;
    onSelectFile?: (file?: FileEntry) => void;
}
declare const FileList: ({ setPath, folder, extensions, onOpen, onSelectFile, selectedFile, }: Props) => JSX.Element;
export default FileList;
