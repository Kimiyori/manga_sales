import React from "react";
import { act } from "react-dom/test-utils";
import ItemDescription from "../ItemDescription";
import { render, cleanup } from "@testing-library/react";

afterEach(cleanup);

describe("ItemDescription", () => {
  it("renders with a name", () => {
    act(() => {
      render(<ItemDescription name={"test"} />);
    });
    expect(document.body.textContent).toBe("test");
  });
  it("renders without a name", () => {
    act(() => {
      render(<ItemDescription />);
    });
    expect(document.body.textContent).toBe("");
  });
});
