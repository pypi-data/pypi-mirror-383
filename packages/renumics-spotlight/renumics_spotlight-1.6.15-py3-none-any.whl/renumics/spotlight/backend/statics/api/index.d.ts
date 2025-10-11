import { FilebrowserApi, LayoutApi, PluginsApi, TableApi, IssuesApi } from '../client';
import { parseError } from './errors';
declare const _default: {
    table: TableApi;
    filebrowser: FilebrowserApi;
    layout: LayoutApi;
    plugin: PluginsApi;
    issues: IssuesApi;
    parseError: typeof parseError;
};
export default _default;
