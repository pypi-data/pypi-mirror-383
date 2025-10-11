import { Widget } from '../../widgets/types';
interface Props {
    addWidget: (widget: Widget) => void;
}
declare const AddWidgetDropdown: ({ addWidget }: Props) => JSX.Element;
export default AddWidgetDropdown;
