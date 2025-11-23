import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

const CsvUpload = () => {
  const [file, setFile] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("/api/upload-csv", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setJobId(data.job_id);
      setStatus("pending");
      setLogs([]);
      pollJobStatus(data.job_id);
    } catch (err) {
      setStatus("error");
      setLogs([err.message]);
    }
    setUploading(false);
  };

  const pollJobStatus = async (jobId) => {
    let done = false;
    while (!done) {
      await new Promise((r) => setTimeout(r, 1500));
      const res = await fetch(`/api/jobs/${jobId}`);
      const data = await res.json();
      setStatus(data.status);
      setLogs(data.logs || []);
      if (data.status === "finished" || data.status === "failed") {
        done = true;
      }
    }
  };

  return (
    <Card className="bg-dashboard-card border-dashboard-border w-full my-8">
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
