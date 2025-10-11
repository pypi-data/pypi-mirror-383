import { Message } from './types';
declare class Connection {
    #private;
    url: string;
    socket?: WebSocket;
    messageQueue: string[];
    onmessage?: (data: unknown) => void;
    constructor(host: string, port: string, basePath: string);
    send(message: Message): void;
}
export default Connection;
