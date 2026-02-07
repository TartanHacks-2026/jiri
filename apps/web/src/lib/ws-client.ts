import {
  type JiriInboundEvent,
  type JiriOutboundMessage,
  parseInboundEvent,
  parseOutboundMessage,
} from "@/lib/event-contract";

export type LiveConnectionStatus = "connected" | "degraded" | "disconnected";

interface StreamCallbacks {
  onEvent: (event: JiriInboundEvent) => void;
  onStatus: (status: LiveConnectionStatus) => void;
  onError: (message: string) => void;
}

interface StreamOptions extends StreamCallbacks {
  wsUrl: string;
  sseUrl?: string;
}

export class JiriStreamClient {
  private ws?: WebSocket;
  private sse?: EventSource;
  private readonly options: StreamOptions;
  private intentionallyClosed = false;

  constructor(options: StreamOptions) {
    this.options = options;
  }

  connect() {
    this.intentionallyClosed = false;

    try {
      this.ws = new WebSocket(this.options.wsUrl);
    } catch (error) {
      this.options.onError(`WebSocket init failed: ${String(error)}`);
      this.fallbackToSse();
      return;
    }

    this.ws.onopen = () => {
      this.options.onStatus("connected");
    };

    this.ws.onmessage = (event) => {
      this.handleInboundData(event.data);
    };

    this.ws.onerror = () => {
      this.options.onError("WebSocket error. Trying fallback...");
      this.fallbackToSse();
    };

    this.ws.onclose = () => {
      if (this.intentionallyClosed) {
        this.options.onStatus("disconnected");
        return;
      }

      this.fallbackToSse();
    };
  }

  send(message: JiriOutboundMessage) {
    const parsed = parseOutboundMessage(message);
    if (!parsed) {
      this.options.onError("Outbound message rejected by schema validation.");
      return;
    }

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(parsed));
      return;
    }

    this.options.onError("Live socket is not connected; message was not sent.");
  }

  close() {
    this.intentionallyClosed = true;
    this.ws?.close();
    this.sse?.close();
    this.options.onStatus("disconnected");
  }

  private fallbackToSse() {
    this.ws?.close();
    this.ws = undefined;

    const sseUrl = this.options.sseUrl ?? deriveSseUrl(this.options.wsUrl);
    if (!sseUrl) {
      this.options.onStatus("degraded");
      this.options.onError("SSE fallback URL is unavailable.");
      return;
    }

    this.options.onStatus("degraded");

    try {
      this.sse = new EventSource(sseUrl);
    } catch (error) {
      this.options.onError(`SSE fallback failed: ${String(error)}`);
      return;
    }

    this.sse.onmessage = (event) => {
      this.handleInboundData(event.data);
    };

    this.sse.onerror = () => {
      this.options.onError("SSE fallback disconnected.");
    };
  }

  private handleInboundData(raw: unknown) {
    let json: unknown;
    try {
      json = typeof raw === "string" ? JSON.parse(raw) : raw;
    } catch {
      this.options.onError("Incoming message is not valid JSON.");
      return;
    }

    const parsed = parseInboundEvent(json);
    if (!parsed) {
      this.options.onError("Incoming event rejected by schema validation.");
      return;
    }

    this.options.onEvent(parsed);
  }
}

export function deriveSseUrl(wsUrl: string) {
  if (!wsUrl) {
    return "";
  }

  try {
    const url = new URL(wsUrl);
    url.protocol = url.protocol === "wss:" ? "https:" : "http:";
    url.pathname = url.pathname.replace(/\/ws$/, "/events");
    return url.toString();
  } catch {
    return "";
  }
}
