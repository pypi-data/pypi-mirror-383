import { DataType } from '../../datatypes';
interface Props<T extends DataType = DataType> {
    value: any;
    type: T;
    placeholder: string;
    onChange?: (value: any) => void;
    onEnter?: (value: any) => void;
}
type FactoryProps = Omit<Props, 'type'> & {
    type?: DataType;
};
declare const ValueInput: (props: FactoryProps) => JSX.Element;
export default ValueInput;
