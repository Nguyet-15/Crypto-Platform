import type { Health, ModuleStatus, Readiness } from '../types/api';
export type { Health } from '../types/api';

export class ApiError extends Error {
  constructor(message: string, public readonly status?: number, public readonly requestId?: string) {
    super(message);
    this.name = 'ApiError';
  }
}
type Options = { baseUrl?: string; timeoutMs?: number; fetcher?: typeof fetch };
const record = (v: unknown): v is Record<string, unknown> => typeof v === 'object' && v !== null;

export function createApiClient({
  baseUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1',
  timeoutMs = 10000, fetcher = fetch,
}: Options = {}) {
  async function get<T>(path: string, valid: (v: unknown) => v is T, signal?: AbortSignal): Promise<T> {
    const controller = new AbortController();
    const abort = () => controller.abort();
    signal?.addEventListener('abort', abort, { once: true });
    if (signal?.aborted) abort();
    const timer = setTimeout(abort, timeoutMs);
    try {
      const response = await fetcher(`${baseUrl.replace(/\/$/, '')}${path}`, {
        cache: 'no-store', signal: controller.signal,
      });
      const id = response.headers.get('X-Request-ID') ?? undefined;
      if (!response.ok) throw new ApiError(`API HTTP ${response.status}`, response.status, id);
      const data: unknown = await response.json();
      if (!valid(data)) throw new ApiError('Invalid API response', response.status, id);
      return data;
    } catch (error) {
      if (error instanceof ApiError) throw error;
      if (signal?.aborted) throw new ApiError('Request cancelled');
      if (controller.signal.aborted) throw new ApiError('API request timed out');
      throw new ApiError('Cannot connect to or read API response');
    } finally {
      clearTimeout(timer);
      signal?.removeEventListener('abort', abort);
    }
  }
  return {
    getHealth: (signal?: AbortSignal) => get<Health>('/health', (v): v is Health =>
      record(v) && v.status === 'ok' && typeof v.service === 'string' && typeof v.version === 'string', signal),
    getReadiness: (signal?: AbortSignal) => get<Readiness>('/health/ready', (v): v is Readiness =>
      record(v) && v.status === 'ready' && v.database === 'ok', signal),
    getModules: (signal?: AbortSignal) => get<ModuleStatus[]>('/modules', (v): v is ModuleStatus[] =>
      Array.isArray(v) && v.every((m: unknown) => record(m) && typeof m.name === 'string' &&
        m.status === 'not_implemented' && typeof m.description === 'string'), signal),
  };
}
export const { getHealth, getReadiness, getModules } = createApiClient();
