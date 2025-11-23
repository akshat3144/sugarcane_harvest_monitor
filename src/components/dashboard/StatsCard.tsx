import { Card } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string;
  icon: LucideIcon;
  subtitle?: string;
  trend?: string;
  trendUp?: boolean;
}

export const StatsCard = ({
  title,
  value,
  icon: Icon,
  subtitle,
  trend,
  trendUp,
}: StatsCardProps) => {
  return (
    <Card className="bg-dashboard-card border-dashboard-border p-4">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs text-white uppercase tracking-wide">{title}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
          {subtitle && <p className="text-xs text-white/80">{subtitle}</p>}
          {trend && (
            <p
              className={`text-xs font-medium ${
                trendUp ? "text-success" : "text-danger"
              } text-white/80`}
            >
              {trendUp ? "↑" : "↓"} {trend}
            </p>
          )}
        </div>
        <div className="rounded-lg bg-primary/10 p-3">
          <Icon className="h-5 w-5 text-primary" />
        </div>
      </div>
    </Card>
  );
};
