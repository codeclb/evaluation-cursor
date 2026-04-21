export interface UploadResponse {
  file_id: string;
  filename: string;
  uploaded_at: string;
}

export interface FileListItem {
  file_id: string;
  filename: string;
  uploaded_at: string;
}

export interface FileMetadataResponse {
  file_id: string;
  filename: string;
  uploaded_at: string;
  has_transformation: boolean;
}

export interface WordCountResponse {
  file_id: string;
  word: string;
  count: number;
}
