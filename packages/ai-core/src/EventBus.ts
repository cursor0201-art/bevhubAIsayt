import { EventEmitter } from 'events';

export interface EventPayload {
  taskId: string;
  type: string;
  sender: string;
  timestamp: number;
  data: any;
}

export type EventCallback = (payload: EventPayload) => void;

export class EventBus {
  private static instance: EventBus;
  private emitter: EventEmitter;

  private constructor() {
    this.emitter = new EventEmitter();
  }

  public static getInstance(): EventBus {
    if (!EventBus.instance) {
      EventBus.instance = new EventBus();
    }
    return EventBus.instance;
  }

  public publish(event: EventPayload): void {
    console.log(`[EventBus] [${event.sender}] Published event '${event.type}' for task ${event.taskId}`);
    this.emitter.emit(event.type, event);
    this.emitter.emit('*', event);
  }

  public subscribe(eventType: string, callback: EventCallback): void {
    this.emitter.on(eventType, callback);
  }

  public unsubscribe(eventType: string, callback: EventCallback): void {
    this.emitter.off(eventType, callback);
  }
}
