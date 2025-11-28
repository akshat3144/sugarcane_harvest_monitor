import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

const metricOptions = [
  { value: "area", label: "Area (acres)" },
  { value: "count", label: "No. of Farms" },
  { value: "percent", label: "% of Farms" },
];

type HarvestChartProps = {
  refreshKey?: number;
};

export const HarvestChart = ({ refreshKey }: HarvestChartProps) => {
  const [metric, setMetric] = useState("area");
  const [data, setData] = useState<{ name: string; value: number }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const API_BASE_URL =
      import.meta.env.VITE_API_URL || "http://localhost:8000/api";
    setLoading(true);
    fetch(
      `${API_BASE_URL}/harvest_chart/harvest-area-timeline?metric=${metric}`
    )
      .then((res) => res.json())
      .then((chart) => {
        setData(
          chart.labels.map((name: string, i: number) => ({
            name,
            value: chart.values[i],
          }))
        );
        setLoading(false);
      });
  }, [metric, refreshKey]);

  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs text-white/80">Show by:</span>
        <select
          className="bg-dashboard-card border border-dashboard-border text-xs text-white rounded px-2 py-1 outline-none"
          value={metric}
          onChange={(e) => setMetric(e.target.value)}
        >
          {metricOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="hsl(var(--chart-grid))"
          />
          <XAxis
            dataKey="name"
            stroke="hsl(var(--muted-foreground))"
            fontSize={12}
          />
          <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--dashboard-card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
            }}
          />
          <Bar dataKey="value" fill="#22c55e" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
