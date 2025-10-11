export interface Message {
    type: string;
    data: unknown;
}
export type MessageHandler = (data: any) => void;
