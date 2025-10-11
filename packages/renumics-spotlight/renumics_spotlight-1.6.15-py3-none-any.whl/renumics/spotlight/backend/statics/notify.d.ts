import { ReactElement } from 'react';
import { TypeOptions } from 'react-toastify';
import { Problem } from './types';
export declare const notify: (message?: string | ReactElement, type?: TypeOptions) => void;
export declare const notifyError: (message: string | ReactElement) => void;
export declare const notifyProblem: (problem: Problem, type?: TypeOptions) => void;
export declare function notifyAPIError(error: any): void;
