import { useCallback, useEffect, useState } from "react";

import { fetchFiles, fetchWordCount, uploadTxtFile } from "./api";
import FileSelector from "./components/FileSelector";
import UploadForm from "./components/UploadForm";
import WordQuery from "./components/WordQuery";
import type { FileListItem, WordCountResponse } from "./types";

function App() {
  const [files, setFiles] = useState<FileListItem[]>([]);
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);
  const [wordCountResult, setWordCountResult] = useState<WordCountResponse | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  const loadFiles = useCallback(async () => {
    try {
      const result = await fetchFiles();
      setFiles(result);
    } catch {
      // silently fail; list stays empty
    }
  }, []);

  useEffect(() => {
    loadFiles();
  }, [loadFiles]);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setUploadError(null);
    setSearchError(null);
    setWordCountResult(null);

    try {
      const result = await uploadTxtFile(file);
      await loadFiles();
      setSelectedFileId(result.file_id);
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  const handleSearch = async (word: string) => {
    if (!selectedFileId) {
      return;
    }

    setIsSearching(true);
    setSearchError(null);

    try {
      const result = await fetchWordCount(selectedFileId, word);
      setWordCountResult(result);
    } catch (error) {
      setWordCountResult(null);
      setSearchError(error instanceof Error ? error.message : "Search failed");
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10 text-slate-900">
      <div className="mx-auto max-w-2xl space-y-4">
        <h1 className="text-3xl font-bold tracking-tight">TXT Analyzer</h1>
        <p className="text-slate-600">Upload a text file and query how many times a word appears.</p>

        <UploadForm isUploading={isUploading} onUpload={handleUpload} />

        {uploadError ? <p className="text-sm font-medium text-red-700">{uploadError}</p> : null}

        <FileSelector
          files={files}
          selectedFileId={selectedFileId}
          onSelect={(id) => {
            setSelectedFileId(id);
            setWordCountResult(null);
            setSearchError(null);
          }}
        />

        <WordQuery disabled={!selectedFileId} isSearching={isSearching} onSearch={handleSearch} />

        {searchError ? <p className="text-sm font-medium text-red-700">{searchError}</p> : null}

        {wordCountResult ? (
          <section className="rounded-lg border border-emerald-400 bg-white p-4 shadow-sm">
            <h2 className="text-lg font-semibold">Result</h2>
            <p className="mt-2 text-slate-700">
              The word <strong>{wordCountResult.word}</strong> appears <strong>{wordCountResult.count}</strong> time(s).
            </p>
          </section>
        ) : null}
      </div>
    </main>
  );
}

export default App;
