import { FormEvent, useEffect, useState } from "react";

type UploadResponse = {
  filename: string;
  uploaded_at: string;
  replaced: boolean;
};

type WordCountResponse = {
  filename: string;
  word: string;
  count: number;
};

type UploadFileListResponse = {
  filenames: string[];
};

type ApiError = {
  detail?: string;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");

  const [filename, setFilename] = useState("");
  const [word, setWord] = useState("");
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryError, setQueryError] = useState("");
  const [queryResult, setQueryResult] = useState<WordCountResponse | null>(null);
  const [fileOptions, setFileOptions] = useState<string[]>([]);
  const [fileOptionsError, setFileOptionsError] = useState("");

  const loadFileOptions = async () => {
    setFileOptionsError("");
    try {
      const response = await fetch(`${API_BASE}/uploads/files`);
      const payload = (await response.json()) as UploadFileListResponse & ApiError;
      if (!response.ok) {
        throw new Error(payload.detail || "Failed to fetch files");
      }
      setFileOptions(payload.filenames);
    } catch (error) {
      setFileOptionsError(error instanceof Error ? error.message : "Failed to fetch files");
    }
  };

  useEffect(() => {
    void loadFileOptions();
  }, []);

  const handleUpload = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    setUploadError("");
    setUploadSuccess("");

    if (!file) {
      setUploadError("Please select a .txt file.");
      return;
    }

    if (!file.name.toLowerCase().endsWith(".txt")) {
      setUploadError("Only .txt files are supported.");
      return;
    }

    setUploadLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/uploads`, {
        method: "POST",
        body: formData,
      });

      const payload = (await response.json()) as UploadResponse & ApiError;
      if (!response.ok) {
        throw new Error(payload.detail || "Upload failed");
      }

      setUploadSuccess(
        payload.replaced
          ? `Replaced existing file '${payload.filename}'.`
          : `Saved new file '${payload.filename}'.`,
      );
      setFilename(payload.filename);
      setFile(null);
      form.reset();
      await loadFileOptions();
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setUploadLoading(false);
    }
  };

  const handleQuery = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setQueryError("");
    setQueryResult(null);

    const trimmedFilename = filename.trim();
    const trimmedWord = word.trim();

    if (!trimmedFilename || !trimmedWord) {
      setQueryError("Filename and word are required.");
      return;
    }

    setQueryLoading(true);
    try {
      const query = new URLSearchParams({ filename: trimmedFilename, word: trimmedWord }).toString();
      const response = await fetch(`${API_BASE}/uploads/count?${query}`);
      const payload = (await response.json()) as WordCountResponse & ApiError;
      if (!response.ok) {
        throw new Error(payload.detail || "Lookup failed");
      }
      setQueryResult(payload);
    } catch (error) {
      setQueryError(error instanceof Error ? error.message : "Lookup failed");
    } finally {
      setQueryLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 py-10 px-4 text-slate-800">
      <div className="mx-auto max-w-2xl space-y-6">
        <h1 className="text-3xl font-bold">TXT Analyzer</h1>

        <section className="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
          <h2 className="mb-4 text-xl font-semibold">Upload TXT File</h2>
          <form onSubmit={handleUpload} className="space-y-3">
            <input
              type="file"
              accept=".txt,text/plain"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
            />
            <button
              type="submit"
              disabled={uploadLoading}
              className="rounded-lg bg-blue-600 px-4 py-2 text-white disabled:bg-slate-400"
            >
              {uploadLoading ? "Uploading..." : "Upload"}
            </button>
          </form>
          {uploadError ? <p className="mt-3 text-sm text-red-600">{uploadError}</p> : null}
          {uploadSuccess ? <p className="mt-3 text-sm text-green-700">{uploadSuccess}</p> : null}
        </section>

        <section className="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
          <h2 className="mb-4 text-xl font-semibold">Find Word Count</h2>
          <form onSubmit={handleQuery} className="space-y-3">
            <label className="block space-y-1">
              <span className="text-sm font-medium">Filename</span>
              <select
                value={filename}
                onChange={(event) => setFilename(event.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2"
              >
                <option value="">Select a file</option>
                {fileOptions.map((name) => (
                  <option key={name} value={name}>
                    {name}
                  </option>
                ))}
              </select>
            </label>
            {fileOptionsError ? <p className="text-sm text-red-600">{fileOptionsError}</p> : null}
            <label className="block space-y-1">
              <span className="text-sm font-medium">Word</span>
              <input
                type="text"
                value={word}
                onChange={(event) => setWord(event.target.value)}
                placeholder="Enter word"
                className="w-full rounded-lg border border-slate-300 px-3 py-2"
              />
            </label>
            <button
              type="submit"
              disabled={queryLoading}
              className="rounded-lg bg-blue-600 px-4 py-2 text-white disabled:bg-slate-400"
            >
              {queryLoading ? "Searching..." : "Get Count"}
            </button>
          </form>
          {queryError ? <p className="mt-3 text-sm text-red-600">{queryError}</p> : null}
          {queryResult ? (
            <p className="mt-3 text-sm text-green-700">
              Word "{queryResult.word}" appears {queryResult.count} time(s) in "{queryResult.filename}".
            </p>
          ) : null}
        </section>
      </div>
    </main>
  );
}
