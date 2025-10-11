import { ConfigApi } from '../client';
export declare class ConfigService {
    api: ConfigApi;
    constructor();
    get<T>(name: string): Promise<T>;
    getItem<T>(name: string): Promise<T>;
    set<T>(name: string, value: T): Promise<void>;
    setItem<T>(name: string, value: T): Promise<void>;
    remove(name: string): Promise<void>;
    removeItem(name: string): Promise<void>;
}
declare const configService: ConfigService;
export default configService;
