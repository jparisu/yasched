import { useState, useRef, useEffect } from "react";
import { ZoomIn, ZoomOut, Maximize2, AlertCircle } from "lucide-react";
import { fetchApi, type Topic } from "@/api/client";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

// ---------------------------------------------------------------------------
// Graph data model
// ---------------------------------------------------------------------------

interface GraphNode {
  id: string;
  label: string;
  color: string;
  x: number;
  y: number;
  radius: number;
}

interface Edge {
  from: string;
  to: string;
}

const NODE_COLORS = [
  "#3b82f6", "#10b981", "#8b5cf6", "#ec4899", "#f59e0b",
  "#ef4444", "#14b8a6", "#6366f1", "#f97316", "#06b6d4",
];

// Hierarchical layout: BFS from roots → assign depths → spread horizontally
function buildGraph(topics: Topic[]): { nodes: GraphNode[]; edges: Edge[] } {
  if (topics.length === 0) return { nodes: [], edges: [] };

  const topicMap = new Map(topics.map((t) => [t.id, t]));

  const depths = new Map<string, number>();
  const queue: [string, number][] = topics
    .filter((t) => t.parent_ids.length === 0)
    .map((t) => [t.id, 0]);

  while (queue.length > 0) {
    const [id, depth] = queue.shift()!;
    if (depths.has(id)) continue;
    depths.set(id, depth);
    topicMap.get(id)?.children_ids.forEach((cid) => queue.push([cid, depth + 1]));
  }
  // Fallback for disconnected nodes
  topics.forEach((t) => { if (!depths.has(t.id)) depths.set(t.id, 0); });

  const byDepth = new Map<number, string[]>();
  depths.forEach((depth, id) => {
    const arr = byDepth.get(depth) ?? [];
    arr.push(id);
    byDepth.set(depth, arr);
  });

  const LEVEL_HEIGHT = 150;
  const H_GAP = 170;
  const START_Y = 80;
  const CENTER_X = 500;

  const positions = new Map<string, { x: number; y: number }>();
  byDepth.forEach((ids, depth) => {
    const startX = CENTER_X - ((ids.length - 1) * H_GAP) / 2;
    ids.forEach((id, i) => {
      positions.set(id, { x: startX + i * H_GAP, y: START_Y + depth * LEVEL_HEIGHT });
    });
  });

  const nodes: GraphNode[] = topics.map((topic, i) => {
    const pos = positions.get(topic.id) ?? { x: CENTER_X, y: START_Y };
    const color =
      topic.effective_layout?.backgrounds?.[0]?.color ??
      NODE_COLORS[i % NODE_COLORS.length];
    const radius =
      topic.parent_ids.length === 0 ? 48 : topic.children_ids.length > 0 ? 40 : 32;
    return { id: topic.id, label: topic.name, color, x: pos.x, y: pos.y, radius };
  });

  const edges: Edge[] = [];
  topics.forEach((t) => t.children_ids.forEach((cid) => edges.push({ from: t.id, to: cid })));

  return { nodes, edges };
}

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max - 1) + "…" : s;
}

// ---------------------------------------------------------------------------
// Topics page
// ---------------------------------------------------------------------------

export function Topics() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchApi<Topic[]>("/topics")
      .then(setTopics)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Unknown error"))
      .finally(() => setLoading(false));
  }, []);

  const { nodes, edges } = buildGraph(topics);
  const topicMap = new Map(topics.map((t) => [t.id, t]));
  const nodeMap = new Map(nodes.map((n) => [n.id, n]));

  const getConnected = (id: string): Set<string> => {
    const s = new Set<string>();
    edges.forEach((e) => {
      if (e.from === id) s.add(e.to);
      if (e.to === id) s.add(e.from);
    });
    return s;
  };

  const handleMouseDown = (e: React.MouseEvent<SVGSVGElement>) => {
    const tag = (e.target as SVGElement).tagName;
    if (tag === "svg" || tag === "line") {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };
  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (isDragging) setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
  };
  const handleMouseUp = () => setIsDragging(false);
  const handleWheel = (e: React.WheelEvent<SVGSVGElement>) => {
    e.preventDefault();
    setZoom((z) => Math.min(Math.max(z - e.deltaY * 0.001, 0.3), 3));
  };

  const selectedTopic = selectedNode ? topicMap.get(selectedNode) : null;
  const selectedGNode = selectedNode ? nodeMap.get(selectedNode) : null;

  if (error) {
    return (
      <div className="p-8 flex items-center gap-3 text-destructive">
        <AlertCircle className="w-5 h-5" />
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col p-6 bg-gradient-to-br from-background via-muted/20 to-background">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground mb-1">Topics</h1>
          <p className="text-muted-foreground text-sm">Topic hierarchy graph</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setZoom((z) => Math.max(z - 0.2, 0.3))}
            className="p-2 bg-card hover:bg-muted rounded-lg transition-colors border border-border shadow-sm"
            title="Zoom Out"
          >
            <ZoomOut className="w-5 h-5" />
          </button>
          <button
            onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}
            className="p-2 bg-card hover:bg-muted rounded-lg transition-colors border border-border shadow-sm"
            title="Reset View"
          >
            <Maximize2 className="w-5 h-5" />
          </button>
          <button
            onClick={() => setZoom((z) => Math.min(z + 0.2, 3))}
            className="p-2 bg-card hover:bg-muted rounded-lg transition-colors border border-border shadow-sm"
            title="Zoom In"
          >
            <ZoomIn className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Graph container */}
      <div className="flex-1 bg-card rounded-xl shadow-lg border border-border overflow-hidden relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex flex-col items-center gap-6">
              <Skeleton className="w-32 h-32 rounded-full" />
              <div className="flex gap-8">
                <Skeleton className="w-20 h-20 rounded-full" />
                <Skeleton className="w-20 h-20 rounded-full" />
                <Skeleton className="w-20 h-20 rounded-full" />
              </div>
            </div>
          </div>
        )}

        {!loading && topics.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-muted-foreground text-sm">
            No topics found.
          </div>
        )}

        {!loading && topics.length > 0 && (
          <>
            {/* Info overlay */}
            <div className="absolute top-4 left-4 bg-background/90 backdrop-blur-sm rounded-lg p-3 shadow-lg z-10 border border-border">
              <p className="text-xs text-muted-foreground mb-1">Zoom: {(zoom * 100).toFixed(0)}%</p>
              <p className="text-xs text-muted-foreground">Drag to pan · Scroll to zoom</p>
              {selectedTopic && (
                <p className="text-xs font-medium mt-2" style={{ color: selectedGNode?.color }}>
                  {selectedTopic.name}
                </p>
              )}
            </div>

            {/* SVG Graph */}
            <svg
              ref={svgRef}
              className="w-full h-full cursor-grab active:cursor-grabbing"
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              onWheel={handleWheel}
              onClick={() => setSelectedNode(null)}
            >
              <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
                {/* Edges */}
                {edges.map((edge, i) => {
                  const from = nodeMap.get(edge.from);
                  const to = nodeMap.get(edge.to);
                  if (!from || !to) return null;
                  const lit =
                    selectedNode === edge.from || selectedNode === edge.to ||
                    hoveredNode === edge.from || hoveredNode === edge.to;
                  return (
                    <line
                      key={i}
                      x1={from.x} y1={from.y} x2={to.x} y2={to.y}
                      stroke={lit ? "#10b981" : "#cbd5e1"}
                      strokeWidth={lit ? 3 : 1}
                      strokeOpacity={lit ? 0.85 : 0.1}
                      className="transition-all duration-300"
                    />
                  );
                })}

                {/* Nodes */}
                {nodes.map((node) => {
                  const isSelected = selectedNode === node.id;
                  const isHovered = hoveredNode === node.id;
                  const connected = selectedNode ? getConnected(selectedNode) : new Set<string>();
                  const dimmed = !!selectedNode && !isSelected && !connected.has(node.id);
                  const connCount = getConnected(node.id).size;

                  return (
                    <g
                      key={node.id}
                      className="cursor-pointer"
                      onMouseEnter={() => setHoveredNode(node.id)}
                      onMouseLeave={() => setHoveredNode(null)}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedNode(isSelected ? null : node.id);
                      }}
                    >
                      {/* Glow */}
                      {(isSelected || isHovered) && (
                        <circle cx={node.x} cy={node.y} r={node.radius + 10}
                          fill={node.color} opacity={0.2} className="animate-pulse" />
                      )}

                      {/* Main circle */}
                      <circle
                        cx={node.x} cy={node.y} r={node.radius}
                        fill={node.color}
                        opacity={dimmed ? 0.25 : 1}
                        stroke={isSelected ? "#10b981" : "white"}
                        strokeWidth={isSelected ? 4 : 2}
                        style={{
                          filter: isHovered ? "brightness(1.15)" : "brightness(1)",
                          transition: "all 0.3s",
                        }}
                      />

                      {/* Label */}
                      <text
                        x={node.x} y={node.y}
                        textAnchor="middle" dominantBaseline="middle"
                        fill="white"
                        fontSize={node.radius > 44 ? 13 : 11}
                        fontWeight="600"
                        opacity={dimmed ? 0.25 : 1}
                        className="pointer-events-none select-none"
                      >
                        {truncate(node.label, node.radius > 44 ? 12 : 10)}
                      </text>

                      {/* Connection count badge */}
                      <circle
                        cx={node.x + node.radius - 8} cy={node.y - node.radius + 8}
                        r={11} fill="white" opacity={dimmed ? 0.25 : 0.95}
                      />
                      <text
                        x={node.x + node.radius - 8} y={node.y - node.radius + 8}
                        textAnchor="middle" dominantBaseline="middle"
                        fontSize={9} fontWeight="700" fill={node.color}
                        opacity={dimmed ? 0.25 : 1}
                        className="pointer-events-none select-none"
                      >
                        {connCount}
                      </text>
                    </g>
                  );
                })}
              </g>
            </svg>

            {/* Detail panel */}
            {selectedTopic && selectedGNode && (
              <div className="absolute bottom-4 left-4 right-4 bg-background/95 backdrop-blur-sm rounded-lg p-4 shadow-lg border border-border">
                <div className="flex items-start gap-4">
                  <div
                    className="w-10 h-10 rounded-full flex-shrink-0 border-2 border-white/20"
                    style={{ backgroundColor: selectedGNode.color }}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-foreground">{selectedTopic.name}</p>
                    {selectedTopic.description && (
                      <p className="text-sm text-muted-foreground mt-0.5">{selectedTopic.description}</p>
                    )}
                    <div className="mt-2 flex flex-wrap items-center gap-3">
                      {selectedTopic.tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
                      ))}
                      {selectedTopic.parent_ids.length > 0 && (
                        <span className="flex items-center gap-1">
                          <span className="text-xs text-muted-foreground">Parents:</span>
                          {selectedTopic.parent_ids.map((pid) => {
                            const pn = nodeMap.get(pid);
                            const pt = topicMap.get(pid);
                            return pn && pt ? (
                              <button
                                key={pid}
                                className="px-2 py-0.5 rounded text-xs font-medium"
                                style={{
                                  backgroundColor: pn.color + "20",
                                  color: pn.color,
                                  border: `1px solid ${pn.color}40`,
                                }}
                                onClick={() => setSelectedNode(pid)}
                              >
                                {pt.name}
                              </button>
                            ) : null;
                          })}
                        </span>
                      )}
                      {selectedTopic.children_ids.length > 0 && (
                        <span className="flex items-center gap-1">
                          <span className="text-xs text-muted-foreground">Children:</span>
                          {selectedTopic.children_ids.map((cid) => {
                            const cn = nodeMap.get(cid);
                            const ct = topicMap.get(cid);
                            return cn && ct ? (
                              <button
                                key={cid}
                                className="px-2 py-0.5 rounded text-xs font-medium"
                                style={{
                                  backgroundColor: cn.color + "20",
                                  color: cn.color,
                                  border: `1px solid ${cn.color}40`,
                                }}
                                onClick={() => setSelectedNode(cid)}
                              >
                                {ct.name}
                              </button>
                            ) : null;
                          })}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
