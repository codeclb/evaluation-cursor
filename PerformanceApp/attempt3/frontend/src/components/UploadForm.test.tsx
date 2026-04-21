import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import UploadForm from "./UploadForm";

describe("UploadForm", () => {
  it("shows an error when submit is pressed without selecting a file", async () => {
    const onUpload = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(<UploadForm isUploading={false} onUpload={onUpload} />);

    await user.click(screen.getByRole("button", { name: "Upload" }));

    expect(screen.getByText("Select a .txt file first.")).toBeInTheDocument();
    expect(onUpload).not.toHaveBeenCalled();
  });

  it("rejects non-txt files", async () => {
    const onUpload = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup({ applyAccept: false });
    const invalidFile = new File(["csv-data"], "data.csv", { type: "text/csv" });

    render(<UploadForm isUploading={false} onUpload={onUpload} />);
    const fileInput = document.querySelector("input[type='file']") as HTMLInputElement;
    expect(fileInput).toBeTruthy();

    await user.upload(fileInput, invalidFile);
    await user.click(screen.getByRole("button", { name: "Upload" }));

    expect(screen.getByText("Only .txt files are supported.")).toBeInTheDocument();
    expect(onUpload).not.toHaveBeenCalled();
  });

  it("calls onUpload with a valid txt file", async () => {
    const onUpload = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    const validFile = new File(["hello world"], "hello.txt", { type: "text/plain" });

    render(<UploadForm isUploading={false} onUpload={onUpload} />);
    const fileInput = document.querySelector("input[type='file']") as HTMLInputElement;
    expect(fileInput).toBeTruthy();

    await user.upload(fileInput, validFile);
    await user.click(screen.getByRole("button", { name: "Upload" }));

    expect(onUpload).toHaveBeenCalledTimes(1);
    expect(onUpload).toHaveBeenCalledWith(validFile);
  });
});
