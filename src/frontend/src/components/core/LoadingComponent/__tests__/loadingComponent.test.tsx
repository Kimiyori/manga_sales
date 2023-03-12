import React from "react";
import { act } from "react-dom/test-utils";
import LoadingComponent from "../loadingComponent";
import { render, cleanup, screen } from "@testing-library/react";

afterEach(cleanup);

describe("LoadingComponent", () => {
  it("renders without crushing", () => {
    act(() => {
      render(<LoadingComponent />);
    });
    expect(screen).toBeDefined();
  });
  it("renders elements", () => {
    act(() => {
      render(<LoadingComponent />);
    });
    expect(document.querySelector(".spin")).toBeDefined();
  });
});
