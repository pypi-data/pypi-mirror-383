import { WebsocketService } from './websocket';
interface ResponseHandler {
    resolve: (result: unknown) => void;
    reject: (error: unknown) => void;
}
declare class TaskService {
    dispatchTable: Map<string, ResponseHandler>;
    websocketService: WebsocketService;
    constructor(websocketService: WebsocketService);
    run(task: string, name: string, args: unknown): Promise<any>;
}
declare const taskService: TaskService;
export default taskService;
