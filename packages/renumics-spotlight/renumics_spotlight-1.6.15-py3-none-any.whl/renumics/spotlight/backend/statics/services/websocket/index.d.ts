import Connection from './connection';
import { Message, MessageHandler } from './types';
export declare class WebsocketService {
    connection: Connection;
    messageHandlers: Map<string, MessageHandler>;
    constructor(host: string, port: string, basePath: string);
    registerMessageHandler(messageType: string, handler: MessageHandler): void;
    send(message: Message): void;
}
declare const websocketService: WebsocketService;
export default websocketService;
