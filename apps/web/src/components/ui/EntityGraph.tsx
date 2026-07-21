/* eslint-disable react-refresh/only-export-components -- shared edge styles + graph colocated */
import { useMemo, useRef, useState } from 'react';
import { GraphData } from '../../api/client';
import { computeLayout, focusSubgraph, NODE_W, HEADER } from '../../lib/graphLayout';
import { tintRgba } from '../../lib/colors';

export type EntityKind = 'topics' | 'tasks' | 'events';

export const EDGE_STYLE: Record<
  string,
  { color: string; dash?: string; marker: string; label: string }
> = {
  requires: { color: '#ef4444', dash: '6 4', marker: 'url(#arrowOpen)', label: 'requires' },
  needs: { color: '#f59e0b', dash: '6 4', marker: 'url(#arrowOpen)', label: 'needs' },
  connected: { color: '#94a3b8', marker: '', label: 'connected' },
  similar: { color: '#94a3b8', dash: '2 4', marker: '', label: 'similar' },
  subtask: { color: '#8b5cf6', marker: 'url(#arrowOpen)', label: 'subtask' },
  event_link: { color: '#0ea5e9', dash: '5 4', marker: 'url(#arrowOpen)', label: 'event link' },
  suboccurrence: { color: '#14b8a6', marker: 'url(#arrowOpen)', label: 'sub-event' },
};

const MARGIN = 20;

interface Props {
  graph: GraphData;
  collapsed?: Set<string>;
  onToggleCollapse?: (topicId: string) => void;
  focusId?: string | null;
  zoom?: number;
  onOpenEntity?: (kind: EntityKind, id: string) => void;
  onOpenElement?: (kind: EntityKind, id: string) => void;
  maxHeight?: string;
}

function trim(
  from: { x: number; y: number },
  to: { x: number; y: number },
  by: number
): { x: number; y: number } {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const len = Math.hypot(dx, dy) || 1;
  return { x: to.x - (dx / len) * by, y: to.y - (dy / len) * by };
}

export function EntityGraph({
  graph,
  collapsed,
  onToggleCollapse,
  focusId = null,
  zoom = 1,
  onOpenEntity,
  onOpenElement,
  maxHeight = 'calc(100vh - 16rem)',
}: Props) {
  const [hover, setHover] = useState<string | null>(null);
  // Defer single-click so a double-click doesn't also open the editor.
  const clickTimer = useRef<number | null>(null);
  const single = (fn: () => void) => {
    if (clickTimer.current) window.clearTimeout(clickTimer.current);
    clickTimer.current = window.setTimeout(() => {
      clickTimer.current = null;
      fn();
    }, 220);
  };
  const double = (fn: () => void) => {
    if (clickTimer.current) {
      window.clearTimeout(clickTimer.current);
      clickTimer.current = null;
    }
    fn();
  };

  const include = useMemo(
    () => (focusId ? focusSubgraph(graph, focusId) : null),
    [graph, focusId]
  );

  const layout = useMemo(
    () =>
      computeLayout(graph, {
        collapsed,
        includeTopics: include ? include.topics : null,
        includeNodes: include ? include.nodes : null,
      }),
    [graph, collapsed, include]
  );

  const topicColor = new Map(graph.topics.map((t) => [t.id, t.color]));
  const nodeColor = (topicId: string | null) =>
    (topicId && topicColor.get(topicId)) || '#94a3b8';

  const W = layout.width + 2 * MARGIN;
  const H = layout.height + 2 * MARGIN;

  return (
    <div
      className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-auto"
      style={{ maxHeight }}
    >
      {/* Rendered at natural px size (not stretched to the container) so label
          text stays a constant size no matter how large the layout grows; the
          zoom control scales everything uniformly. */}
      <svg viewBox={`0 0 ${W} ${H}`} width={W} height={H} style={{ zoom }}>
        <defs>
          <marker id="arrowOpen" markerWidth="12" markerHeight="12" refX="9" refY="5" orient="auto" markerUnits="userSpaceOnUse">
            <path d="M1,1 L10,5 L1,9" fill="none" stroke="context-stroke" strokeWidth="1.6" />
          </marker>
        </defs>

        <g transform={`translate(${MARGIN}, ${MARGIN})`}>
          {/* topic boxes (outermost first) */}
          {layout.boxes.map((b) => {
            const focused = b.id === focusId;
            const editable = b.id !== '__unassigned__';
            return (
              <g key={b.id}>
                <rect
                  x={b.x}
                  y={b.y}
                  width={b.w}
                  height={b.h}
                  rx={12}
                  fill={tintRgba(b.color, b.depth === 0 ? 0.06 : 0.12)}
                  stroke={b.color}
                  strokeOpacity={focused ? 1 : 0.55}
                  strokeWidth={focused ? 3 : 1.5}
                  style={{ cursor: editable ? 'pointer' : 'default' }}
                  onClick={() => editable && single(() => onOpenEntity?.('topics', b.id))}
                  onDoubleClick={() => editable && double(() => onOpenElement?.('topics', b.id))}
                />
                {/* header label */}
                <text
                  x={b.x + 30}
                  y={b.y + HEADER / 2 + 4}
                  style={{ fontSize: 13, fontWeight: 700, pointerEvents: 'none' }}
                  fill={b.color}
                >
                  {b.name}
                  {b.collapsed && b.count > 0 ? `  (${b.count})` : ''}
                </text>
                {/* collapse / expand toggle */}
                {(b.count > 0 || b.collapsed) && onToggleCollapse && editable && (
                  <g
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleCollapse(b.id);
                    }}
                    style={{ cursor: 'pointer' }}
                  >
                    <rect x={b.x + 8} y={b.y + HEADER / 2 - 8} width={16} height={16} rx={4} fill={b.color} fillOpacity={0.18} />
                    <text
                      x={b.x + 16}
                      y={b.y + HEADER / 2 + 4}
                      textAnchor="middle"
                      style={{ fontSize: 12, fontWeight: 800, pointerEvents: 'none' }}
                      fill={b.color}
                    >
                      {b.collapsed ? '+' : '–'}
                    </text>
                  </g>
                )}
              </g>
            );
          })}

          {/* connection edges (node → node) */}
          {graph.edges.map((e, i) => {
            const s = layout.nodeCenters.get(e.source);
            const t = layout.nodeCenters.get(e.target);
            if (!s || !t) return null;
            const style = EDGE_STYLE[e.type] ?? EDGE_STYLE.connected;
            const a = trim(t, s, NODE_W / 2 - 6);
            const b = trim(s, t, NODE_W / 2 - 6);
            const dim = hover && hover !== e.source && hover !== e.target;
            return (
              <line
                key={`e-${i}`}
                x1={a.x}
                y1={a.y}
                x2={b.x}
                y2={b.y}
                stroke={style.color}
                strokeWidth={1.8}
                strokeDasharray={style.dash}
                markerEnd={style.marker || undefined}
                opacity={dim ? 0.12 : 0.9}
              />
            );
          })}

          {/* member nodes (tasks / events) */}
          {layout.nodes.map(({ node, x, y, w, h }) => {
            const color = nodeColor(node.topicId);
            const focused = node.id === focusId;
            const dim = hover && hover !== node.id;
            const short = node.label.length > 17 ? node.label.slice(0, 16) + '…' : node.label;
            const kind: EntityKind = node.kind === 'task' ? 'tasks' : 'events';
            return (
              <g
                key={node.id}
                onMouseEnter={() => setHover(node.id)}
                onMouseLeave={() => setHover(null)}
                onClick={() => single(() => onOpenEntity?.(kind, node.id))}
                onDoubleClick={() => double(() => onOpenElement?.(kind, node.id))}
                style={{ cursor: 'pointer' }}
                opacity={dim ? 0.4 : 1}
              >
                <title>{node.label}</title>
                <rect
                  x={x}
                  y={y}
                  width={w}
                  height={h}
                  rx={node.kind === 'task' ? 9 : 3}
                  className="fill-white dark:fill-slate-800"
                  stroke={color}
                  strokeWidth={focused ? 3 : 2}
                />
                <rect x={x} y={y} width={5} height={h} rx={2} fill={color} />
                <text
                  x={x + w / 2 + 2}
                  y={y + h / 2 + 4}
                  textAnchor="middle"
                  style={{ fontSize: 10.5, pointerEvents: 'none' }}
                  className="fill-slate-700 dark:fill-slate-200"
                >
                  {node.kind === 'task' ? '▭ ' : '◆ '}
                  {short}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
}
