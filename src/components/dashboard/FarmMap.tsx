import { MapContainer, TileLayer, Polygon, Popup, useMap } from "react-leaflet";
import { LatLngExpression, LatLngBounds } from "leaflet";
import { useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import "leaflet/dist/leaflet.css";

interface Farm {
  id: string;
  name: string;
  village: string;
  area: number;
  recentNDVI: number;
  prevNDVI: number;
  harvest: number;
  bounds: LatLngExpression[];
}

interface FarmMapProps {
  farms: Farm[];
  getHealthColor: (ndvi: number) => string;
}

function AutoFitBounds({ farms }: { farms: Farm[] }) {
  const map = useMap();
  useEffect(() => {
    if (farms.length === 0) return;
    // Flatten all bounds
    const allPoints = farms.flatMap((f) => f.bounds);
    if (allPoints.length === 0) return;
    const bounds = new LatLngBounds(allPoints as [number, number][]);
    map.fitBounds(bounds, { padding: [30, 30] });
  }, [farms, map]);
  return null;
}

export const FarmMap = ({ farms, getHealthColor }: FarmMapProps) => {
  // Use green for harvest, red for not harvest
  const getHarvestColor = (harvest: number) =>
    harvest === 1 ? "#22c55e" : "#ef4444";
  return (
    <div className="relative h-full w-full">
      {/* Legend moved to bottom left */}
      <div
        style={{
          position: "absolute",
          zIndex: 1000,
          bottom: 16,
          left: 16,
          background: "rgba(30,41,59,0.85)",
          borderRadius: 8,
          padding: "8px 16px",
          display: "flex",
          gap: 16,
          alignItems: "center",
          color: "white",
          fontSize: 14,
        }}
      >
        <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span
            style={{
              width: 16,
              height: 16,
              background: "#22c55e",
              borderRadius: 4,
              display: "inline-block",
              border: "1px solid #16a34a",
            }}
          ></span>
          Harvest Ready
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span
            style={{
              width: 16,
              height: 16,
              background: "#ef4444",
              borderRadius: 4,
              display: "inline-block",
              border: "1px solid #b91c1c",
            }}
          ></span>
          Not Ready
        </span>
      </div>
      <MapContainer
        center={[19.237, 73.124]}
        zoom={13}
        className="h-full w-full"
        style={{ background: "hsl(var(--dashboard-card))" }}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        <AutoFitBounds farms={farms} />
        {farms.map((farm) => (
          <Polygon
            key={farm.id}
            positions={farm.bounds}
            pathOptions={{
              color: getHarvestColor(farm.harvest),
              fillColor: getHarvestColor(farm.harvest),
              fillOpacity: 0.6,
              weight: 2,
            }}
          >
            <Popup>
              <div className="p-2 min-w-[200px] text-white">
                <h3 className="font-bold mb-2 text-white">{farm.name}</h3>
                <div className="space-y-1 text-sm">
                  <p>
                    <span className="font-medium text-white/80">Farm ID:</span>{" "}
                    <span className="text-white/90">{farm.id}</span>
                  </p>
                  <p>
                    <span className="font-medium text-white/80">Village:</span>{" "}
                    <span className="text-white/90">{farm.village}</span>
                  </p>
                  <p>
                    <span className="font-medium text-white/80">Area:</span>{" "}
                    <span className="text-white/90">{farm.area} acres</span>
                  </p>
                  <p>
                    <span className="font-medium text-white/80">
                      Recent NDVI:
                    </span>{" "}
                    <span className="text-white/90">{farm.recentNDVI}</span>
                  </p>
                  <p>
                    <span className="font-medium text-white/80">
                      Previous NDVI:
                    </span>{" "}
                    <span className="text-white/90">{farm.prevNDVI}</span>
                  </p>
                  <p>
                    <span className="font-medium text-white/80">Change:</span>{" "}
                    <span className="text-white/90">
                      {(farm.recentNDVI - farm.prevNDVI).toFixed(3)}
                    </span>
                  </p>
                  <div className="mt-2">
                    {farm.harvest === 1 ? (
                      <Badge
                        style={{ backgroundColor: "#22c55e", color: "white" }}
                      >
                        Harvest Ready
                      </Badge>
                    ) : (
                      <Badge
                        style={{ backgroundColor: "#ef4444", color: "white" }}
                      >
                        Not Ready
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </Popup>
          </Polygon>
        ))}
      </MapContainer>
    </div>
  );
};
