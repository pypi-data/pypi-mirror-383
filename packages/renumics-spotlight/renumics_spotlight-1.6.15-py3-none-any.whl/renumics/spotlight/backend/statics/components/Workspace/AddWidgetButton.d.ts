import type { IconType } from 'react-icons';
interface Props {
    name: string;
    icon: IconType;
    experimental?: boolean;
    onClick: () => void;
}
declare const AddWidgetButton: ({ name, icon, experimental, onClick, }: Props) => JSX.Element;
export default AddWidgetButton;
