import { PCANormalization } from '../../services/data';
interface Props {
    pcaNormalization: PCANormalization;
    onChangePcaNormalization: (value?: PCANormalization) => void;
}
export declare const PCAParameterMenu: ({ pcaNormalization, onChangePcaNormalization, }: Props) => JSX.Element;
export {};
