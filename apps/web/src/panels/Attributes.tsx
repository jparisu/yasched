import { useData } from '../store';
import { PanelCard } from '../ui/PanelCard';

export function Attributes() {
  const { definitions } = useData();
  const builtin = definitions.filter((d) => d.builtin);
  const custom = definitions.filter((d) => !d.builtin);

  return (
    <div className="space-y-4">
      <PanelCard
        title="Custom attributes"
        subtitle="Defined in the database `attributes` section"
        collapseId="attr-custom"
      >
        {custom.length === 0 ? (
          <p className="text-sm text-slate-400">
            No custom attributes yet. Add them under the top-level <code>attributes:</code> key in
            your database file (type, applies_to, min/max, enum_values, layout).
          </p>
        ) : (
          <DefTable defs={custom} />
        )}
      </PanelCard>

      <PanelCard title="Built-in attributes" collapseId="attr-builtin" defaultCollapsed>
        <DefTable defs={builtin} />
      </PanelCard>
    </div>
  );
}

function DefTable({
  defs,
}: {
  defs: {
    name: string;
    valueType: string;
    appliesTo: string[];
    inherits: boolean;
    enumValues?: string[];
    min?: number;
    max?: number;
  }[];
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-400 border-b border-slate-200 dark:border-slate-700">
            <th className="py-1.5 pr-4 font-medium">Name</th>
            <th className="py-1.5 pr-4 font-medium">Type</th>
            <th className="py-1.5 pr-4 font-medium">Applies to</th>
            <th className="py-1.5 pr-4 font-medium">Range / values</th>
            <th className="py-1.5 font-medium">Inherits</th>
          </tr>
        </thead>
        <tbody>
          {defs.map((d) => (
            <tr key={d.name} className="border-b border-slate-100 dark:border-slate-800">
              <td className="py-1.5 pr-4 font-mono">{d.name}</td>
              <td className="py-1.5 pr-4 text-slate-500">{d.valueType}</td>
              <td className="py-1.5 pr-4 text-slate-500">
                {d.appliesTo.length ? d.appliesTo.join(', ') : 'all'}
              </td>
              <td className="py-1.5 pr-4 text-slate-500">
                {d.enumValues?.length
                  ? d.enumValues.join(' | ')
                  : d.min != null || d.max != null
                    ? `${d.min ?? ''}…${d.max ?? ''}`
                    : '—'}
              </td>
              <td className="py-1.5 text-slate-500">{d.inherits ? 'yes' : 'no'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
