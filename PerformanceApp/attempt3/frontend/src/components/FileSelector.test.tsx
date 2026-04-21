import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import FileSelector from "./FileSelector";

describe("FileSelector", () => {
  it("renders uploaded files and notifies selection", async () => {
    const onSelect = vi.fn();
    const user = userEvent.setup();

    render(
      <FileSelector
        files={[
          { file_id: "1", filename: "alpha.txt", uploaded_at: "2026-04-16T12:00:00Z" },
          { file_id: "2", filename: "beta.txt", uploaded_at: "2026-04-16T13:00:00Z" },
        ]}
        selectedFileId={null}
        onSelect={onSelect}
      />,
    );

    const select = screen.getByRole("combobox");
    await user.selectOptions(select, "2");

    expect(onSelect).toHaveBeenCalledWith("2");
    expect(screen.getByText(/alpha\.txt/)).toBeInTheDocument();
    expect(screen.getByText(/beta\.txt/)).toBeInTheDocument();
  });
});
