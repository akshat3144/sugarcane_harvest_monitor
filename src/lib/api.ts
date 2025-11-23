/**
 * API client for FastAPI backend
 * Update API_BASE_URL to your backend server
 */

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export interface Farm {
  id: string;
  name: string;
  village: string;
  area: number;
  recentNDVI: number;
  prevNDVI: number;
  harvest: number;
  bounds: [number, number][];
}

export interface StatsData {
  total_farms: number;
  harvest_ready_count: number;
  harvest_ready_percentage: number;
  avg_ndvi: number;
  avg_ndvi_change: number;
  total_area: number;
  total_harvest_area: number;
}

export interface ChartData {
  labels: string[];
  values: number[];
  colors?: string[];
}

/**
 * Fetch all farms as GeoJSON
 */
export const fetchFarmsGeoJSON = async (village?: string) => {
  const url = new URL(`${API_BASE_URL}/farms`);
  if (village) {
    url.searchParams.append("village", village);
  }
  url.searchParams.append("page_size", "5000"); // Always fetch all farms

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error("Failed to fetch farms");
  }

  return response.json();
};

/**
 * Fetch summary statistics
 */
export const fetchStats = async (village?: string): Promise<StatsData> => {
  const url = new URL(`${API_BASE_URL}/stats/summary`);
  if (village) {
    url.searchParams.append("village", village);
  }

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error("Failed to fetch stats");
  }

  return response.json();
};

/**
 * Fetch village statistics
 */
export const fetchVillageStats = async () => {
  const response = await fetch(`${API_BASE_URL}/stats/by-village`);
  if (!response.ok) {
    throw new Error("Failed to fetch village stats");
  }

  return response.json();
};

/**
 * Fetch NDVI chart data
 */
export const fetchNDVIChart = async (): Promise<ChartData> => {
  const response = await fetch(`${API_BASE_URL}/charts/ndvi-by-village`);
  if (!response.ok) {
    throw new Error("Failed to fetch NDVI chart data");
  }

  return response.json();
};

/**
 * Fetch harvest area chart data
 */
export const fetchHarvestChart = async (): Promise<ChartData> => {
  const response = await fetch(`${API_BASE_URL}/charts/harvest-area-timeline`);
  if (!response.ok) {
    throw new Error("Failed to fetch harvest chart data");
  }

  return response.json();
};

/**
 * Fetch health distribution data
 */
export const fetchHealthDistribution = async (): Promise<ChartData> => {
  const response = await fetch(`${API_BASE_URL}/charts/health-distribution`);
  if (!response.ok) {
    throw new Error("Failed to fetch health distribution");
  }

  return response.json();
};

/**
 * Get single farm details
 */
export const fetchFarm = async (farmId: string) => {
  const response = await fetch(`${API_BASE_URL}/farms/${farmId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch farm details");
  }

  return response.json();
};

/**
 * Upload CSV file
 */
export const uploadFarmCSV = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/farms/upload-csv`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to upload CSV");
  }

  return response.json();
};
