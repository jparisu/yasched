import { useCallback, useEffect, useState } from 'react';
import { DisplayStyle } from '../types';

export interface PanelConfig {
  view: DisplayStyle;
  zoom: number;
  // Extra per-panel UI state (used by panels that need it, e.g. Task Board's
  // grouping axes and resize toggle). Persisted alongside view/zoom.
  resize: boolean;
  columnMode: string;
  rowMode: string;
}

const DEFAULTS: PanelConfig = {
  view: 'square',
  zoom: 1,
  resize: true,
  columnMode: 'stage',
  rowMode: 'time',
};
export const ZOOM_MIN = 0.4;
export const ZOOM_MAX = 2;
const ZOOM_STEP = 0.1;

/**
 * Per-panel UI preferences (display style + zoom), persisted to localStorage
 * under a panel-specific key so each panel remembers its own configuration
 * independently of the others.
 */
export function usePanelConfig(key: string, overrides: Partial<PanelConfig> = {}) {
  const storageKey = `yasched-panel-${key}`;

  const [config, setConfig] = useState<PanelConfig>(() => {
    const base = { ...DEFAULTS, ...overrides };
    try {
      const saved = localStorage.getItem(storageKey);
      return saved ? { ...base, ...JSON.parse(saved) } : base;
    } catch {
      return base;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(config));
    } catch {
      /* ignore quota/availability errors */
    }
  }, [storageKey, config]);

  const update = useCallback(
    (partial: Partial<PanelConfig>) => setConfig((c) => ({ ...c, ...partial })),
    []
  );
  const setView = useCallback((view: DisplayStyle) => update({ view }), [update]);
  const setZoom = useCallback(
    (zoom: number) => update({ zoom: Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, zoom)) }),
    [update]
  );
  const zoomBy = useCallback((delta: number) => setZoom(config.zoom + delta), [config.zoom, setZoom]);
  const stepZoom = useCallback((dir: 1 | -1) => zoomBy(dir * ZOOM_STEP), [zoomBy]);

  return { config, update, view: config.view, setView, zoom: config.zoom, setZoom, stepZoom };
}
