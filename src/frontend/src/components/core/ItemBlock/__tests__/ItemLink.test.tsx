import React from "react";
import { act } from "react-dom/test-utils";
import ItemLink from "../ItemLink";
import { render, cleanup } from "@testing-library/react";

afterEach(cleanup);

describe("ItemLink", () => {
  it("renders with a link", () => {
    act(() => {
      render(<ItemLink link={"test"} />);
    });
    expect(document.body.textContent).toBe(" Official Website");
  });
});
