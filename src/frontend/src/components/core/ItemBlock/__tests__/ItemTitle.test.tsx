import React from "react";
import { act } from "react-dom/test-utils";
import ItemTitle from "../ItemTitle";
import { render, cleanup } from "@testing-library/react";

afterEach(cleanup);

describe("ItemTitle", () => {
  it("renders name", () => {
    act(() => {
      render(<ItemTitle name={"test"} link={"test"} />);
    });
    expect(document.querySelector(".title")?.textContent).toBe("test");
  });
  it("renders link", () => {
    act(() => {
      render(<ItemTitle name={"test"} link={"test"} />);
    });
    expect(document.body.querySelector(".link")?.textContent).toBe(" Official Website");
  });
  it("renders icon link", () => {
    act(() => {
      render(<ItemTitle name={"test"} link={"test"} />);
    });
    expect(document.body.querySelector("svg")).toBeDefined();
  });
});
