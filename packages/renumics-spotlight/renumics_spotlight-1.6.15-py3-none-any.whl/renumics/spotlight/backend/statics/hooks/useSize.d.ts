import { RefObject } from 'react';
interface Size {
    width: number;
    height: number;
}
declare const useSize: (ref: RefObject<HTMLElement>) => Size;
export default useSize;
