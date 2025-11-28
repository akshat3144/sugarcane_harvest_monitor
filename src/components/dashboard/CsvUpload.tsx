import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

type CsvUploadProps = {
  onUploadComplete?: () => void;
};

const CsvUpload: React.FC<CsvUploadProps> = ({ onUploadComplete }) => {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const API_BASE_URL =
        import.meta.env.VITE_API_URL || "http://localhost:8000/api";
      const res = await fetch(`${API_BASE_URL}/upload-csv`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setJobId(data.job_id);
      setStatus("pending");
      setLogs([]);
      pollJobStatus(data.job_id);
    } catch (err: any) {
      setStatus("error");
      setLogs([err.message]);
    }
    setUploading(false);
  };

  const pollJobStatus = async (jobId: string) => {
    const API_BASE_URL =
      import.meta.env.VITE_API_URL || "http://localhost:8000/api";
    let done = false;
    while (!done) {
      await new Promise((r) => setTimeout(r, 1500));
      const res = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
      const data = await res.json();
      setStatus(data.status);
      setLogs(data.logs || []);
      if (data.status === "finished" || data.status === "failed") {
        done = true;
        if (data.status === "finished" && onUploadComplete) {
          onUploadComplete();
        }
      }
    }
  };

  return (
    <Card className="bg-dashboard-card border-dashboard-border w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg text-white">Upload Farm CSV</CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex items-center gap-2 mb-2">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="block flex-1 text-sm text-white file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-primary/80"
          />
          <button
            className="px-4 py-2 bg-green-600 text-white rounded disabled:opacity-50 transition-colors duration-150"
            onClick={handleUpload}
            disabled={!file || uploading}
          >
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </div>
        {jobId && (
          <div className="mt-4">
            <div className="font-semibold text-white">Job ID: {jobId}</div>
            <div className="text-white">
              Status:{" "}
              <span
                className={
                  status === "finished"
                    ? "text-green-400"
                    : status === "failed"
                    ? "text-red-400"
                    : "text-white"
                }
              >
                {status}
              </span>
            </div>
            <div className="mt-2">
              <div className="font-semibold text-white">Logs:</div>
              <pre className="bg-gray-800 p-2 rounded text-xs max-h-40 overflow-auto text-white">
                {logs.join("\n")}
              </pre>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CsvUpload;
