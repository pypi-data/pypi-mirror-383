interface Props {
    path: string;
    parent?: string;
    setPath: (path: string) => void;
}
declare const AddressBar: ({ path, parent, setPath }: Props) => JSX.Element;
export default AddressBar;
