/// <reference types="react" />
import { LensSettings, Setter } from '../types';
interface LensContextType {
    settings: LensSettings;
    onChangeSettings: Setter<LensSettings>;
    sharedState: Record<string, unknown>;
    setSharedState: Setter<Record<string, unknown>>;
}
declare const LensContext: import("react").Context<LensContextType>;
export default LensContext;
