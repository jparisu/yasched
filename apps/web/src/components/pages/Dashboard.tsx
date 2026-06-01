import { useEffect, useState } from "react";
import { fetchApi, type HealthData, type Topic } from "@/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CalendarDays, CheckSquare, Tag, AlertCircle } from "lucide-react";

// ---------------------------------------------------------------------------
// Topic tree
// ---------------------------------------------------------------------------

function TopicNode({
  topic,
  allTopics,
  depth,
}: {
  topic: Topic;
  allTopics: Map<string, Topic>;
  depth: number;
}) {
  const [open, setOpen] = useState(true);
  const children = topic.children_ids
    .map((id) => allTopics.get(id))
    .filter(Boolean) as Topic[];

  const color =
    topic.effective_layout?.backgrounds?.[0]?.color ?? null;

  return (
    <div style={{ marginLeft: depth * 20 }}>
      <div
        className="flex items-center gap-2 py-1.5 group cursor-pointer"
        onClick={() => children.length > 0 && setOpen(!open)}
      >
        {/* Color swatch */}
        {color ? (
          <span
            className="inline-block w-3 h-3 rounded-full flex-shrink-0 border border-border/40"
            style={{ backgroundColor: color }}
          />
        ) : (
          <span className="inline-block w-3 h-3 rounded-full flex-shrink-0 bg-muted border border-border/40" />
        )}

        {/* Expand indicator */}
        {children.length > 0 && (
          <span className="text-muted-foreground text-xs w-3 select-none">
            {open ? "▾" : "▸"}
          </span>
        )}
        {children.length === 0 && <span className="w-3" />}

        <span className="text-sm font-medium text-foreground">{topic.name}</span>

        {topic.tags.map((tag) => (
          <Badge key={tag} variant="secondary" className="text-xs py-0">
            {tag}
          </Badge>
        ))}

        {topic.description && (
          <span className="text-xs text-muted-foreground hidden group-hover:inline ml-1">
            — {topic.description}
          </span>
        )}
      </div>

      {open &&
        children.map((child) => (
          <TopicNode
            key={child.id}
            topic={child}
            allTopics={allTopics}
            depth={depth + 1}
          />
        ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Stat card
// ---------------------------------------------------------------------------

function StatCard({
  title,
  value,
  icon: Icon,
  sub,
}: {
  title: string;
  value: number;
  icon: React.ElementType;
  sub?: string;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          <Icon className="w-4 h-4 text-muted-foreground" />
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-semibold">{value}</p>
        {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
      </CardContent>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export function Dashboard() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchApi<HealthData>("/health"),
      fetchApi<Topic[]>("/topics"),
    ])
      .then(([h, t]) => {
        setHealth(h);
        setTopics(t);
      })
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Unknown error"),
      )
      .finally(() => setLoading(false));
  }, []);

  if (error) {
    return (
      <div className="p-8 flex items-center gap-3 text-destructive">
        <AlertCircle className="w-5 h-5" />
        <span>{error}</span>
      </div>
    );
  }

  // Build topic map for tree rendering
  const topicMap = new Map(topics.map((t) => [t.id, t]));
  const rootTopics = topics.filter((t) => t.parent_ids.length === 0);

  const s = health?.status_summary;
  const activeCount = (s?.todo ?? 0) + (s?.in_progress ?? 0) + (s?.blocked ?? 0);

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Overview of your scheduler database
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-3 gap-4">
        {loading ? (
          <>
            <Skeleton className="h-28 rounded-xl" />
            <Skeleton className="h-28 rounded-xl" />
            <Skeleton className="h-28 rounded-xl" />
          </>
        ) : (
          <>
            <StatCard
              title="Tasks"
              value={health!.task_count}
              icon={CheckSquare}
              sub={`${activeCount} active · ${s?.done ?? 0} done`}
            />
            <StatCard
              title="Events"
              value={health!.event_count}
              icon={CalendarDays}
            />
            <StatCard
              title="Topics"
              value={health!.topic_count}
              icon={Tag}
            />
          </>
        )}
      </div>

      {/* Task status breakdown */}
      {!loading && health && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Task Status</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            {Object.entries(health.status_summary).map(([status, count]) => (
              <div key={status} className="flex items-center gap-2">
                <Badge
                  variant={
                    status === "done"
                      ? "default"
                      : status === "blocked" || status === "cancelled"
                        ? "destructive"
                        : "secondary"
                  }
                >
                  {status.replace("_", " ")}
                </Badge>
                <span className="text-sm font-medium">{count}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Topic tree */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Topics</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              <Skeleton className="h-5 w-48" />
              <Skeleton className="h-5 w-64 ml-5" />
              <Skeleton className="h-5 w-56 ml-5" />
              <Skeleton className="h-5 w-40" />
            </div>
          ) : rootTopics.length === 0 ? (
            <p className="text-muted-foreground text-sm">No topics found.</p>
          ) : (
            <div>
              {rootTopics.map((t) => (
                <TopicNode key={t.id} topic={t} allTopics={topicMap} depth={0} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
