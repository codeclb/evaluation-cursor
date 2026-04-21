import type { ChangeEvent } from "react";

import type { FileListItem } from "../types";

interface FileSelectorProps {
  files: FileListItem[];
  selectedFileId: string | null;
  onSelect: (fileId: string | null) => void;
  disabled?: boolean;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString();
}

function FileSelector({ files, selectedFileId, onSelect, disabled }: FileSelectorProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold">Select a File</h2>
      <select
        className="mt-3 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 disabled:cursor-not-allowed disabled:bg-slate-100"
        value={selectedFileId ?? ""}
        onChange={(event: ChangeEvent<HTMLSelectElement>) => onSelect(event.target.value || null)}
        disabled={disabled || files.length === 0}
      >
        <option value="">-- Choose a file --</option>
        {files.map((f) => (
          <option key={f.file_id} value={f.file_id}>
            {f.filename} ({formatDate(f.uploaded_at)})
          </option>
        ))}
      </select>
    </div>
  );
}

export default FileSelector;
