// HTTP client for the v4 API. One process serves this SPA + the API, so all
// requests are same-origin (no CORS, no base URL config).

import {
  EffortDTO,
  ElementSpec,
  MetaDTO,
  PayloadDTO,
  ValidationDTO,
} from './types';

const BASE = '/api';

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`Request failed: ${path} (HTTP ${res.status})`);
  return (await res.json()) as T;
}

async function write(method: string, path: string, body?: unknown): Promise<void> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const data = (await res.json()) as { detail?: unknown };
      if (data?.detail) detail = String(data.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
}

export function fetchElements(start?: string, end?: string): Promise<PayloadDTO> {
  const params = new URLSearchParams();
  if (start) params.set('start', start);
  if (end) params.set('end', end);
  const query = params.toString();
  return getJSON<PayloadDTO>(`/elements${query ? `?${query}` : ''}`);
}

/** The RAW (own, unresolved) element — for editing. 404 for virtual elements. */
export const fetchElement = (id: string): Promise<ElementSpec> =>
  getJSON<ElementSpec>(`/elements/${encodeURIComponent(id)}`);

export const fetchMeta = (): Promise<MetaDTO> => getJSON<MetaDTO>('/meta');
export const fetchValidation = (): Promise<ValidationDTO> => getJSON<ValidationDTO>('/validate');

export function fetchEffort(start?: string, end?: string): Promise<EffortDTO> {
  const params = new URLSearchParams();
  if (start) params.set('start', start);
  if (end) params.set('end', end);
  const query = params.toString();
  return getJSON<EffortDTO>(`/effort${query ? `?${query}` : ''}`);
}

export const createElement = (spec: ElementSpec): Promise<void> =>
  write('POST', '/elements', spec);

export const updateElement = (id: string, spec: Omit<ElementSpec, 'id'>): Promise<void> =>
  write('PUT', `/elements/${encodeURIComponent(id)}`, spec);

export const deleteElement = (id: string): Promise<void> =>
  write('DELETE', `/elements/${encodeURIComponent(id)}`);

export const reloadDatabase = (): Promise<void> => write('POST', '/reload');
