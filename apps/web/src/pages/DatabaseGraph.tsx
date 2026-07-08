import { useState } from 'react';
import { mockGraphNodes } from '../data/mockData';
import { GraphNode } from '../types';
import { GlobalControls } from '../components/ui';
import { DisplayStyle, Density, CardShape } from '../types';

interface DatabaseGraphProps {
  displayStyle: DisplayStyle;
  density: Density;
  cardShape: CardShape;
  onUpdateSettings: (key: string, value: string) => void;
}

const nodeTypeColors: Record<string, string> = {
  task: '#3b82f6',
  event: '#22c55e',
  topic: '#f59e0b',
  subtopic: '#fb923c',
  deadline: '#ef4444',
  style: '#8b5cf6',
  recurring: '#06b6d4',
};

const nodeTypeGradients: Record<string, string> = {
  task: 'from-sky-400 to-sky-600',
  event: 'from-mint-400 to-mint-600',
  topic: 'from-peach-400 to-peach-600',
  subtopic: 'from-lemon-400 to-lemon-600',
  deadline: 'from-coral-400 to-coral-600',
  style: 'from-lavender-400 to-lavender-600',
  recurring: 'from-teal-400 to-teal-600',
};

export function DatabaseGraph({ displayStyle, density, cardShape, onUpdateSettings }: DatabaseGraphProps) {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const offset = { x: 40, y: 40 };
  const scale = 1.2;

  const getNodePosition = (node: GraphNode) => ({
    x: node.x * scale + offset.x,
    y: node.y * scale + offset.y,
  });

  const getNodeConnections = (node: GraphNode) =>
    node.connections
      .map(connId => mockGraphNodes.find(n => n.id === connId))
      .filter(Boolean) as GraphNode[];

  const densityStyles = {
    expanded: { minH: 450, nodeSize: 'p-4 min-w-[140px]' },
    comfortable: { minH: 350, nodeSize: 'p-3 min-w-[120px]' },
    compact: { minH: 250, nodeSize: 'p-2 min-w-[100px]' },
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">
            Information Structure
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Visual representation of how data entities connect
          </p>
        </div>
        <GlobalControls
          displayStyle={displayStyle}
          density={density}
          cardShape={cardShape}
          onDisplayStyleChange={(v) => onUpdateSettings('displayStyle', v)}
          onDensityChange={(v) => onUpdateSettings('density', v)}
          onCardShapeChange={(v) => onUpdateSettings('cardShape', v)}
        />
      </div>

      <div className="rounded-2xl overflow-hidden shadow-lg border border-slate-200/50 dark:border-slate-700 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 relative" style={{ minHeight: densityStyles[density].minH }}>
        <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ minHeight: densityStyles[density].minH }}>
          {mockGraphNodes.map((node) => {
            const sourcePos = getNodePosition(node);
            const connections = getNodeConnections(node);

            return connections.map((targetNode) => {
              const targetPos = getNodePosition(targetNode);
              if (targetPos.x < sourcePos.x) return null;

              const gradientId = `line-${node.id}-${targetNode.id}`;
              return (
                <g key={gradientId}>
                  <defs>
                    <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor={nodeTypeColors[node.type]} stopOpacity="0.6" />
                      <stop offset="100%" stopColor={nodeTypeColors[targetNode.type]} stopOpacity="0.6" />
                    </linearGradient>
                  </defs>
                  <line
                    x1={sourcePos.x + 70}
                    y1={sourcePos.y + 20}
                    x2={targetPos.x}
                    y2={targetPos.y + 20}
                    stroke={`url(#${gradientId})`}
                    strokeWidth="3"
                    strokeLinecap="round"
                  />
                </g>
              );
            });
          })}
        </svg>

        <div className="relative p-6" style={{ minHeight: densityStyles[density].minH }}>
          {mockGraphNodes.map((node) => {
            const position = getNodePosition(node);
            const isSelected = selectedNode?.id === node.id;

            return (
              <button
                key={node.id}
                className={`absolute transition-all duration-300 ${densityStyles[density].nodeSize} ${
                  displayStyle === 'square' ? 'rounded-2xl cloud ' :
                  displayStyle === 'line' ? 'rounded-xl' :
                  'rounded-full'
                } ${isSelected ? 'ring-4 ring-slate-400 ring-offset-2 scale-105' : ''}`}
                style={{
                  left: position.x,
                  top: position.y,
                }}
                onClick={() => setSelectedNode(node)}
              >
                <div className={`bg-gradient-to-br ${nodeTypeGradients[node.type]} text-white shadow-lg ${
                  cardShape === 'sticky' ? 'sticky-shape' :
                  cardShape === 'curvy' ? 'curvy-shape' :
                  cardShape === 'cloudy' ? 'cloudy-shape' :
                  'rounded-xl'
                } ${densityStyles[density].nodeSize} flex flex-col items-center justify-center gap-1`}
                >
                  <span className="text-[10px] font-bold uppercase tracking-wider opacity-80">
                    {node.type}
                  </span>
                  <span className="text-sm font-semibold">{node.label}</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {selectedNode && (
        <div className="rounded-2xl p-5 bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-900 border border-slate-200/50 dark:border-slate-700 shadow-lg">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className={`w-4 h-4 rounded-full bg-gradient-to-br ${nodeTypeGradients[selectedNode.type]}`} />
                <span className="text-xs font-bold uppercase tracking-wide text-slate-500">
                  {selectedNode.type}
                </span>
              </div>
              <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-2">
                {selectedNode.label}
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                {selectedNode.description}
              </p>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors text-2xl"
            >
              &times;
            </button>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
            <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-2">
              Connections ({selectedNode.connections.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {getNodeConnections(selectedNode).map((conn) => (
                <button
                  key={conn.id}
                  onClick={() => setSelectedNode(conn)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all bg-gradient-to-r ${nodeTypeGradients[conn.type]} text-white hover:scale-105`}
                >
                  {conn.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
