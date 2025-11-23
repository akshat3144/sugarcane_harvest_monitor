import { useState, useEffect } from "react";
import { LatLngExpression } from "leaflet";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MapPin, TrendingDown, TrendingUp, Leaf, Users } from "lucide-react";
import { NDVIChart } from "@/components/dashboard/NDVIChart";
import { HarvestChart } from "@/components/dashboard/HarvestChart";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { FarmMap } from "@/components/dashboard/FarmMap";
import CsvUpload from "@/components/dashboard/CsvUpload";
import "leaflet/dist/leaflet.css";
import { fetchFarmsGeoJSON, fetchStats } from "@/lib/api";

const getHealthColor = (ndvi: number) => {
  if (ndvi >= 0.7) return "#22c55e"; // excellent
  if (ndvi >= 0.6) return "#84cc16"; // good
  if (ndvi >= 0.5) return "#eab308"; // moderate
  if (ndvi >= 0.4) return "#f97316"; // poor
  return "#ef4444"; // critical
};

const Dashboard = () => {
  const [selectedCrop, setSelectedCrop] = useState("sugarcane");
  const [selectedVillage, setSelectedVillage] = useState("all");
  const [farms, setFarms] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const loadFarms = async () => {
      setLoading(true);
      try {
        const geojson = await fetchFarmsGeoJSON(
          selectedVillage !== "all" ? selectedVillage : undefined
        );
        // Parse GeoJSON features into FarmMap format
        const parsed = geojson.features.map((f: any) => {
          const coords = f.geometry.coordinates[0].map(
            (c: number[]) => [c[1], c[0]] as LatLngExpression
          );
          return {
            id: f.properties.farm_id || f.properties.id,
            name:
              f.properties.Farmer_Name ||
              f.properties.name ||
              f.properties.farm_id,
            village: f.properties.Vill_Name || f.properties.village,
            area: f.properties.Area || f.properties.area,
            recentNDVI:
              f.properties.recent_ndvi || f.properties.recentNDVI || 0,
            prevNDVI: f.properties.prev_ndvi || f.properties.prevNDVI || 0,
            harvest: f.properties.harvest_flag || f.properties.harvest || 0,
            bounds: coords,
          };
        });
        setFarms(parsed);
      } catch (err) {
        setFarms([]);
      }
      setLoading(false);
    };
    loadFarms();
  }, [selectedVillage, refreshKey]);

  useEffect(() => {
    const loadStats = async () => {
      setStatsLoading(true);
      try {
        const s = await fetchStats(
          selectedVillage !== "all" ? selectedVillage : undefined
        );
        setStats(s);
      } catch (err) {
        setStats(null);
      }
      setStatsLoading(false);
    };
    loadStats();
  }, [selectedVillage, refreshKey]);

  const handleUploadComplete = () => {
    setRefreshKey((k) => k + 1);
  };

  return (
    <div className="min-h-screen bg-dashboard-bg text-foreground">
      {/* Header */}
      <header className="border-b border-dashboard-border bg-dashboard-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Leaf className="h-8 w-8 text-success" />
            <h1 className="text-2xl font-bold text-white">
              Sugarcane Harvest Monitor
            </h1>
          </div>
          <div className="flex items-center gap-4">
            {/* Crop dropdown removed: only sugarcane is available */}
            {/* Village dropdown removed: only one village or no filtering needed */}
            <div className="flex items-center gap-2 rounded-lg bg-background/50 px-4 py-2">
              {stats && stats.avg_ndvi_change >= 0 ? (
                <TrendingUp className="h-5 w-5 text-success" />
              ) : (
                <TrendingDown className="h-5 w-5 text-danger" />
              )}
              <span className="font-semibold text-white">
                {stats
                  ? ((stats.avg_ndvi_change / 0.5) * 100).toFixed(1)
                  : "0.0"}
                %
              </span>
            </div>
          </div>
        </div>
      </header>
      {/* Main Content */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 p-2 md:p-4">
        {/* Left Side - Map */}
        <div className="md:col-span-7 space-y-4 order-1 md:order-1">
          <Card className="h-[300px] md:h-[calc(100vh-200px)] overflow-hidden bg-dashboard-card border-dashboard-border">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                Loading farms...
              </div>
            ) : (
              <FarmMap farms={farms} getHealthColor={getHealthColor} />
            )}
          </Card>
          {/* Stats Row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-4">
            <StatsCard
              title="Total Farms"
              value={
                statsLoading || !stats ? "-" : stats.total_farms.toString()
              }
              icon={MapPin}
              trend=""
            />
            <StatsCard
              title="Avg NDVI"
              value={statsLoading || !stats ? "-" : stats.avg_ndvi.toFixed(3)}
              icon={Leaf}
              trend={
                stats && stats.avg_ndvi_change
                  ? ((stats.avg_ndvi_change / 0.5) * 100).toFixed(1) + "%"
                  : ""
              }
              trendUp={stats && stats.avg_ndvi_change >= 0}
            />
            <StatsCard
              title="Harvest Ready"
              value={
                statsLoading || !stats
                  ? "-"
                  : stats.harvest_ready_count.toString()
              }
              icon={Users}
              subtitle={
                stats && stats.total_farms
                  ? `${(
                      (stats.harvest_ready_count / stats.total_farms) *
                      100
                    ).toFixed(0)}% of farms`
                  : ""
              }
            />
            <StatsCard
              title="NDVI Change"
              value={
                stats && stats.avg_ndvi_change
                  ? ((stats.avg_ndvi_change / 0.5) * 100).toFixed(1) + "%"
                  : "-"
              }
              icon={
                stats && stats.avg_ndvi_change >= 0 ? TrendingUp : TrendingDown
              }
              trendUp={stats && stats.avg_ndvi_change >= 0}
            />
          </div>
          {/* NDVI Health Legend below stats */}
          <Card className="bg-dashboard-card border-dashboard-border p-2 md:p-4 mt-4">
            <h3 className="text-sm font-semibold mb-3 text-white">
              NDVI Health Legend
            </h3>
            <div className="flex flex-wrap gap-x-8 gap-y-3">
              <div className="flex items-center gap-2">
                <div
                  className="h-4 w-4 rounded"
                  style={{ backgroundColor: "#22c55e" }}
                />
                <span className="text-sm text-white">Excellent (≥0.7)</span>
              </div>
              <div className="flex items-center gap-2">
                <div
                  className="h-4 w-4 rounded"
                  style={{ backgroundColor: "#84cc16" }}
                />
                <span className="text-sm text-white">Good (0.6-0.7)</span>
              </div>
              <div className="flex items-center gap-2">
                <div
                  className="h-4 w-4 rounded"
                  style={{ backgroundColor: "#eab308" }}
                />
                <span className="text-sm text-white">Moderate (0.5-0.6)</span>
              </div>
              <div className="flex items-center gap-2">
                <div
                  className="h-4 w-4 rounded"
                  style={{ backgroundColor: "#f97316" }}
                />
                <span className="text-sm text-white">Poor (0.4-0.5)</span>
              </div>
              <div className="flex items-center gap-2">
                <div
                  className="h-4 w-4 rounded"
                  style={{ backgroundColor: "#ef4444" }}
                />
                <span className="text-sm text-white">Critical (&lt;0.4)</span>
              </div>
            </div>
          </Card>
        </div>
        {/* Right Side - Charts & Stats */}
        <div className="md:col-span-5 space-y-4 order-2 md:order-2">
          {/* NDVI Trend Chart */}
          {/* Legend */}
          <Card className="bg-dashboard-card border-dashboard-border p-2 md:p-6">
            <h3 className="text-lg font-semibold mb-4 text-white">
              Average NDVI by Village
            </h3>
            <NDVIChart refreshKey={refreshKey} />
          </Card>
          {/* Harvest Area Chart */}
          <Card className="bg-dashboard-card border-dashboard-border p-2 md:p-6">
            <h3 className="text-lg font-semibold mb-4 text-white">
              Harvest-Ready Area by Village
            </h3>
            <HarvestChart refreshKey={refreshKey} />
          </Card>
          {/* CSV Upload UI */}
          <CsvUpload onUploadComplete={handleUploadComplete} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
