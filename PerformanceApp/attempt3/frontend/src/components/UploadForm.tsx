import { FormEvent, useState } from "react";

interface UploadFormProps {
  isUploading: boolean;
  onUpload: (file: File) => Promise<void>;
}

function UploadForm({ isUploading, onUpload }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!file) {
      setError("Select a .txt file first.");
      return;
    }

    if (!file.name.toLowerCase().endsWith(".txt")) {
      setError("Only .txt files are supported.");
      return;
    }

    setError(null);
    await onUpload(file);
  };

  return (
    <form className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm" onSubmit={onSubmit}>
      <h2 className="text-lg font-semibold">Upload TXT File</h2>
      <input
        className="mt-3 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 file:mr-3 file:rounded-md file:border-0 file:bg-blue-600 file:px-3 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-blue-700"
        type="file"
        accept=".txt,text/plain"
        onChange={(event) => {
          setFile(event.target.files?.[0] ?? null);
          setError(null);
        }}
      />
      {error ? <p className="mt-2 text-sm font-medium text-red-700">{error}</p> : null}
      <button
        className="mt-3 inline-flex w-fit items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
        type="submit"
        disabled={isUploading}
      >
        {isUploading ? "Uploading..." : "Upload"}
      </button>
    </form>
  );
}

export default UploadForm;
