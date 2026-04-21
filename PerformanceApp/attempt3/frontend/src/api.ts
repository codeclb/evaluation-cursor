import type { FileListItem, UploadResponse, WordCountResponse } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function parseError(response: Response): Promise<string> {
  try {
    const payload = await response.json();
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
  } catch (_err) {
    // noop: fallback to status text
  }

  return response.statusText || "Request failed";
}

export async function uploadTxtFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE_URL}/files/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return (await response.json()) as UploadResponse;
}

export async function fetchFiles(): Promise<FileListItem[]> {
  const response = await fetch(`${API_BASE_URL}/files`);

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return (await response.json()) as FileListItem[];
}

export async function fetchWordCount(fileId: string, word: string): Promise<WordCountResponse> {
  const query = new URLSearchParams({ word });
  const response = await fetch(`${API_BASE_URL}/files/${fileId}/count?${query.toString()}`);

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return (await response.json()) as WordCountResponse;
}
