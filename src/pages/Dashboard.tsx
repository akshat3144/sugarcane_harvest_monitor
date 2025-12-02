import { useState, useEffect, useCallback } from "react";
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
  const [currentBbox, setCurrentBbox] = useState<string | undefined>(undefined);
  const [currentZoom, setCurrentZoom] = useState<number>(13);
  const [loadedPages, setLoadedPages] = useState<Set<number>>(new Set());
  const [initialLoadDone, setInitialLoadDone] = useState(false);
  const [loadedBboxes, setLoadedBboxes] = useState<Set<string>>(new Set());
  const [allLoadedFarms, setAllLoadedFarms] = useState<Map<string, any>>(
    new Map()
  );

  // Load initial subset of farms without bbox to get starting location
  const loadInitialFarms = async () => {
    setLoading(true);
    try {
      const geojson = await fetchFarmsGeoJSON(
        selectedVillage !== "all" ? selectedVillage : undefined,
        undefined, // No bbox filter for initial load
        undefined,
        1,
        50 // Start with just 50 farms
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
          recentNDVI: f.properties.recent_ndvi || f.properties.recentNDVI || 0,
          prevNDVI: f.properties.prev_ndvi || f.properties.prevNDVI || 0,
          harvest: f.properties.harvest_flag || f.properties.harvest || 0,
          bounds: coords,
        };
      });

      setFarms(parsed);
      setInitialLoadDone(true);
    } catch (err) {
      console.error("Failed to load initial farms:", err);
      setFarms([]);
    }
    setLoading(false);
  };

  // Check if bbox is significantly different (to avoid reload on tiny movements)
  const isSignificantBboxChange = (
    oldBbox: string,
    newBbox: string
  ): boolean => {
    const [oldMinX, oldMinY, oldMaxX, oldMaxY] = oldBbox.split(",").map(Number);
    const [newMinX, newMinY, newMaxX, newMaxY] = newBbox.split(",").map(Number);

    const oldWidth = oldMaxX - oldMinX;
    const oldHeight = oldMaxY - oldMinY;

    // Consider significant if moved more than 30% of viewport size
    const threshold = 0.3;
    const xDiff = Math.abs(newMinX - oldMinX);
    const yDiff = Math.abs(newMinY - oldMinY);

    return xDiff > oldWidth * threshold || yDiff > oldHeight * threshold;
  };

  // Progressive loading function with streaming updates
  const loadFarmsForViewport = async (
    bbox?: string,
    zoom?: number,
    reset: boolean = false
  ) => {
    if (!bbox || !initialLoadDone) return;

    // Check if we already loaded this bbox (within tolerance)
    if (!reset && loadedBboxes.has(bbox)) {
      console.log("Using cached data for this viewport");
      return;
    }

    // Check if bbox change is significant enough to reload
    if (!reset && loadedBboxes.size > 0) {
      const lastBbox = Array.from(loadedBboxes).pop();
      if (lastBbox && !isSignificantBboxChange(lastBbox, bbox)) {
        console.log("Viewport change too small, skipping reload");
        return;
      }
    }

    if (reset) {
      setLoadedPages(new Set());
      setAllLoadedFarms(new Map());
      setLoadedBboxes(new Set());
    }

    setLoading(true);
    try {
      const newFarmsMap = new Map(allLoadedFarms);

      // Load first page immediately to show something fast
      const firstPage = await fetchFarmsGeoJSON(
        selectedVillage !== "all" ? selectedVillage : undefined,
        bbox,
        zoom,
        1,
        1000
      );

      // Parse and display first batch immediately
      firstPage.features.forEach((f: any) => {
        const coords = f.geometry.coordinates[0].map(
          (c: number[]) => [c[1], c[0]] as LatLngExpression
        );
        const farm = {
          id: f.properties.farm_id || f.properties.id,
          name:
            f.properties.Farmer_Name ||
            f.properties.name ||
            f.properties.farm_id,
          village: f.properties.Vill_Name || f.properties.village,
          area: f.properties.Area || f.properties.area,
          recentNDVI: f.properties.recent_ndvi || f.properties.recentNDVI || 0,
          prevNDVI: f.properties.prev_ndvi || f.properties.prevNDVI || 0,
          harvest: f.properties.harvest_flag || f.properties.harvest || 0,
          bounds: coords,
        };
        newFarmsMap.set(farm.id, farm);
      });

      // Update UI with first batch
      setAllLoadedFarms(new Map(newFarmsMap));
      setFarms(Array.from(newFarmsMap.values()));
      setLoading(false);

      // Load remaining pages in background (max 5 total pages = 5000 farms)
      const totalPages = firstPage.metadata?.total_pages || 1;
      const maxPages = Math.min(totalPages, 5); // Cap at 5 pages for performance

      if (maxPages > 1) {
        // Load remaining pages asynchronously
        for (let page = 2; page <= maxPages; page++) {
          const geojson = await fetchFarmsGeoJSON(
            selectedVillage !== "all" ? selectedVillage : undefined,
            bbox,
            zoom,
            page,
            1000
          );

          geojson.features.forEach((f: any) => {
            const coords = f.geometry.coordinates[0].map(
              (c: number[]) => [c[1], c[0]] as LatLngExpression
            );
            const farm = {
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
            newFarmsMap.set(farm.id, farm);
          });

          // Update UI after each page loads
          setAllLoadedFarms(new Map(newFarmsMap));
          setFarms(Array.from(newFarmsMap.values()));
        }
      }

      setLoadedBboxes((prev) => new Set([...prev, bbox]));
    } catch (err) {
      console.error("Failed to load farms:", err);
      if (reset) {
        setFarms([]);
      }
      setLoading(false);
    }
  };

  // Handle viewport changes with debouncing
  const handleViewportChange = useCallback((bbox: string, zoom: number) => {
    setCurrentBbox(bbox);
    setCurrentZoom(zoom);
  }, []);

  // Load initial farms on mount or when refreshKey changes
  useEffect(() => {
    loadInitialFarms();
  }, [selectedVillage, refreshKey]);

  // Load farms when viewport changes (only after initial load)
  useEffect(() => {
    if (currentBbox && initialLoadDone) {
      const timeoutId = setTimeout(() => {
        loadFarmsForViewport(currentBbox, currentZoom, false);
      }, 800); // Debounce 800ms (increased for better performance)

      return () => clearTimeout(timeoutId);
    }
  }, [currentBbox, currentZoom, selectedVillage, refreshKey, initialLoadDone]);

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
            <FarmMap
              farms={farms}
              getHealthColor={getHealthColor}
              onViewportChange={handleViewportChange}
              initialFitBounds={
                !initialLoadDone || (farms.length > 0 && refreshKey === 0)
              }
            />
            {loading && farms.length === 0 && (
              <div
                style={{
                  position: "absolute",
                  top: "50%",
                  left: "50%",
                  transform: "translate(-50%, -50%)",
                  background: "rgba(30,41,59,0.9)",
                  padding: "12px 24px",
                  borderRadius: "8px",
                  color: "white",
                  zIndex: 1000,
                }}
              >
                Loading initial farms...
              </div>
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
        </div>
        {/* Right Side - Charts & Stats */}
        <div className="md:col-span-5 space-y-4 order-2 md:order-2">
          {/* CSV Upload UI - moved above plots */}
          <CsvUpload onUploadComplete={handleUploadComplete} />
          {/* Harvest Area Chart - moved above NDVI Chart */}
          <Card className="bg-dashboard-card border-dashboard-border p-2 md:p-6">
            <h3 className="text-lg font-semibold mb-4 text-white">
              Harvest-Ready Area by Village
            </h3>
            <HarvestChart refreshKey={refreshKey} />
          </Card>
          {/* NDVI Trend Chart */}
          <Card className="bg-dashboard-card border-dashboard-border p-2 md:p-6">
            <h3 className="text-lg font-semibold mb-4 text-white">
              Average NDVI by Village
            </h3>
            <NDVIChart refreshKey={refreshKey} />
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
