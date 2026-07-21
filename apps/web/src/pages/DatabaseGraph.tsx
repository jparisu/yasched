import { useEffect, useMemo, useState } from 'react';
import { Share2, ChevronsDownUp, ChevronsUpDown } from 'lucide-react';
import { GraphData, fetchGraph } from '../api/client';
import { useEditor } from '../data/EditorContext';
import { useElement } from '../data/ElementContext';
import { usePanelConfig } from '../data/usePanelConfig';
import { ZoomControls } from '../components/ui';
import { EntityGraph, EDGE_STYLE } from '../components/ui/EntityGraph';

export function DatabaseGraph() {
  const { openEdit } = useEditor();
  const { openElement } = useElement();
  const { zoom, stepZoom, setZoom } = usePanelConfig('graph');
  const [graph, setGraph] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchGraph()
      .then(setGraph)
      .finally(() => setLoading(false));
  }, []);

  const toggleCollapse = (id: string) =>
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const usedEdgeTypes = useMemo(
    () => [...new Set((graph?.edges ?? []).map((e) => e.type))].filter((t) => EDGE_STYLE[t]),
    [graph]
  );

  if (loading) return <div className="py-16 text-center text-slate-400">Loading graph…</div>;
  if (!graph) return <div className="py-16 text-center text-slate-400">No graph data.</div>;

  return (
    <div className="max-w-6xl mx-auto space-y-4">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r from-rose-100 to-lemon-100 dark:from-rose-900/30 dark:to-lemon-900/30 text-rose-600 dark:text-rose-400 text-sm font-semibold">
            <Share2 size={16} />
            Database Graph
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Topics are nested boxes; tasks (▭) and events (◆) live inside them. Click to edit,
            double-click to open the element. Use +/– on a topic to fold it.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCollapsed(new Set(graph.topics.map((t) => t.id)))}
            title="Collapse all topics"
            className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-slate-700 dark:hover:text-slate-200"
          >
            <ChevronsDownUp size={16} />
          </button>
          <button
            onClick={() => setCollapsed(new Set())}
            title="Expand all topics"
            className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-slate-700 dark:hover:text-slate-200"
          >
            <ChevronsUpDown size={16} />
          </button>
          <ZoomControls zoom={zoom} onStep={stepZoom} onReset={() => setZoom(1)} />
        </div>
      </div>

      <EntityGraph
        graph={graph}
        collapsed={collapsed}
        onToggleCollapse={toggleCollapse}
        zoom={zoom}
        onOpenEntity={openEdit}
        onOpenElement={openElement}
      />

      <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
        <div className="flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-600 dark:text-slate-300">
          <span className="flex items-center gap-1.5">▭ Task</span>
          <span className="flex items-center gap-1.5">◆ Event</span>
          {usedEdgeTypes.map((t) => (
            <span key={t} className="flex items-center gap-1.5">
              <svg width="30" height="12">
                <line
                  x1="1"
                  y1="6"
                  x2="29"
                  y2="6"
                  stroke={EDGE_STYLE[t].color}
                  strokeWidth="2"
                  strokeDasharray={EDGE_STYLE[t].dash}
                />
              </svg>
              {EDGE_STYLE[t].label}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
