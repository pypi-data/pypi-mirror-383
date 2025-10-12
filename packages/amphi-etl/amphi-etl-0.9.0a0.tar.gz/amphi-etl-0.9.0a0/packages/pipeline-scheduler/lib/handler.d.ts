export declare function requestScheduler<T = any>(endpoint: string, { method, body, stream, signal, init }?: {
    method?: string;
    body?: unknown;
    stream?: boolean;
    signal?: AbortSignal;
    init?: RequestInit;
}): Promise<T | ReadableStreamDefaultReader<Uint8Array>>;
