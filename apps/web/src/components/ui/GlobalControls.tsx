import { ToggleGroup } from './ToggleGroup';
import { DisplayStyle, Density, CardShape } from '../../types';
import { LayoutGrid, AlignLeft, Minimize2, Maximize2, Minus, Square } from 'lucide-react';

interface GlobalControlsProps {
  displayStyle: DisplayStyle;
  density: Density;
  cardShape: CardShape;
  onDisplayStyleChange: (style: DisplayStyle) => void;
  onDensityChange: (density: Density) => void;
  onCardShapeChange: (shape: CardShape) => void;
}

export function GlobalControls({
  displayStyle,
  density,
  cardShape,
  onDisplayStyleChange,
  onDensityChange,
  onCardShapeChange,
}: GlobalControlsProps) {
  return (
    <div className="flex items-center gap-4 flex-wrap">
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-slate-500 dark:text-slate-400">View:</span>
        <div className="flex items-center gap-0.5 p-0.5 bg-slate-100 dark:bg-slate-800 rounded-lg">
          <button
            onClick={() => onDisplayStyleChange('square')}
            className={`p-1.5 rounded-md transition-all ${
              displayStyle === 'square'
                ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
                : 'text-slate-400 hover:text-slate-600'
            }`}
            title="Square/Cards"
          >
            <LayoutGrid size={16} />
          </button>
          <button
            onClick={() => onDisplayStyleChange('line')}
            className={`p-1.5 rounded-md transition-all ${
              displayStyle === 'line'
                ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
                : 'text-slate-400 hover:text-slate-600'
            }`}
            title="Lines"
          >
            <AlignLeft size={16} />
          </button>
          <button
            onClick={() => onDisplayStyleChange('collapsed')}
            className={`p-1.5 rounded-md transition-all ${
              displayStyle === 'collapsed'
                ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
                : 'text-slate-400 hover:text-slate-600'
            }`}
            title="Collapsed"
          >
            <Minimize2 size={16} />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Size:</span>
        <div className="flex items-center gap-0.5 p-0.5 bg-slate-100 dark:bg-slate-800 rounded-lg">
          <button
            onClick={() => onDensityChange('expanded')}
            className={`p-1.5 rounded-md transition-all ${
              density === 'expanded'
                ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
                : 'text-slate-400 hover:text-slate-600'
            }`}
            title="Expanded"
          >
            <Maximize2 size={16} />
          </button>
          <button
            onClick={() => onDensityChange('comfortable')}
            className={`p-1.5 rounded-md transition-all ${
              density === 'comfortable'
                ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
                : 'text-slate-400 hover:text-slate-600'
            }`}
            title="Comfortable"
          >
            <Square size={16} />
          </button>
          <button
            onClick={() => onDensityChange('compact')}
            className={`p-1.5 rounded-md transition-all ${
              density === 'compact'
                ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
                : 'text-slate-400 hover:text-slate-600'
            }`}
            title="Compact"
          >
            <Minus size={16} />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Shape:</span>
        <ToggleGroup
          options={[
            { value: 'rounded', label: 'Round' },
            { value: 'curvy', label: 'Curvy' },
            { value: 'cloudy', label: 'Cloud' },
            { value: 'sticky', label: 'Sticky' },
          ]}
          value={cardShape}
          onChange={(v) => onCardShapeChange(v as CardShape)}
          size="sm"
        />
      </div>
    </div>
  );
}
