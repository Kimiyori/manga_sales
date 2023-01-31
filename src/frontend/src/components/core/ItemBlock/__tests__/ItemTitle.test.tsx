import React from "react";
import { act } from "react-dom/test-utils";
import ItemTitle from "../ItemTitle";
import { render, cleanup } from "@testing-library/react";

afterEach(cleanup);

describe("ItemTitle", () => {
  it("renders with a name", () => {
    act(() => {
      render(<ItemTitle name={"test"} />);
    });
    expect(document.body.textContent).toBe("test");
  });
  it("renders without a name", () => {
    act(() => {
      render(<ItemTitle />);
    });
    expect(document.body.textContent).toBe("");
  });
});
