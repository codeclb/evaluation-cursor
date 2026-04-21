import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import * as api from "./api";

vi.mock("./api", async () => {
  const actual = await vi.importActual<typeof import("./api")>("./api");
  return {
    ...actual,
    fetchFiles: vi.fn(),
    fetchWordCount: vi.fn(),
    uploadTxtFile: vi.fn(),
  };
});

const mockedFetchFiles = vi.mocked(api.fetchFiles);
const mockedFetchWordCount = vi.mocked(api.fetchWordCount);
const mockedUploadTxtFile = vi.mocked(api.uploadTxtFile);

describe("App", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("loads previous files and runs word count on selected file", async () => {
    const user = userEvent.setup();
    mockedFetchFiles.mockResolvedValue([
      { file_id: "file-1", filename: "old.txt", uploaded_at: "2026-04-16T12:00:00Z" },
    ]);
    mockedFetchWordCount.mockResolvedValue({ file_id: "file-1", word: "hello", count: 3 });

    render(<App />);

    await waitFor(() => {
      expect(mockedFetchFiles).toHaveBeenCalledTimes(1);
    });

    await user.selectOptions(screen.getByRole("combobox"), "file-1");
    await user.type(screen.getByPlaceholderText("Enter a single word"), "hello");
    await user.click(screen.getByRole("button", { name: "Count" }));

    await waitFor(() => {
      expect(mockedFetchWordCount).toHaveBeenCalledWith("file-1", "hello");
    });

    expect(screen.getByText("Result")).toBeInTheDocument();
    expect(screen.getByText(/time\(s\)\./)).toBeInTheDocument();
  });

  it("shows upload API errors", async () => {
    const user = userEvent.setup();
    mockedFetchFiles.mockResolvedValue([]);
    mockedUploadTxtFile.mockRejectedValue(new Error("A file named 'dup.txt' has already been uploaded"));

    render(<App />);

    await waitFor(() => {
      expect(mockedFetchFiles).toHaveBeenCalledTimes(1);
    });

    const fileInput = document.querySelector("input[type='file']") as HTMLInputElement;
    const validFile = new File(["hello"], "dup.txt", { type: "text/plain" });

    await user.upload(fileInput, validFile);
    await user.click(screen.getByRole("button", { name: "Upload" }));

    await waitFor(() => {
      expect(screen.getByText("A file named 'dup.txt' has already been uploaded")).toBeInTheDocument();
    });
  });
});
