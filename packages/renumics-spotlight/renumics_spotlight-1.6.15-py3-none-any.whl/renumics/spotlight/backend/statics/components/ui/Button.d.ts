import * as React from 'react';
import { ReactNode } from 'react';
type Size = 'small' | 'medium';
type ExtraProps = {
    outlined?: boolean;
    checked?: boolean;
    size?: Size;
    tooltip?: ReactNode;
};
declare const StyledHTMLButton: import("styled-components").StyledComponent<"button", any, ExtraProps, never>;
export type Props = ExtraProps & Omit<React.ComponentProps<typeof StyledHTMLButton>, 'as' | 'title'>;
declare const _default: React.ForwardRefExoticComponent<Pick<Props, string | number | symbol> & React.RefAttributes<HTMLButtonElement>>;
export default _default;
