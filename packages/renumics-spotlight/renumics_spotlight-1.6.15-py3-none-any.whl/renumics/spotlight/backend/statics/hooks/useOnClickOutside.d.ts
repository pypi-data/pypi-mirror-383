import { MutableRefObject } from 'react';
type ElementRef = MutableRefObject<HTMLElement | null>;
type Callback = (event: Event) => void;
declare function useOnClickOutside(ref: ElementRef, callback?: Callback): void;
export default useOnClickOutside;
