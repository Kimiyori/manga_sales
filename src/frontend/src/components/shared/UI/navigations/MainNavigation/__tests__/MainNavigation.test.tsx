import React from "react";
import { act } from "react-dom/test-utils";
import { render, cleanup, screen } from "@testing-library/react";
import Navbar, { paths } from "../MainNavigation";

afterEach(cleanup);

describe("LoadingComponent", () => {
  it("renders without crushing", () => {
    act(() => {
      render(<Navbar />);
    });
    expect(screen).toBeDefined();
  });
  it("renders elements", () => {
    act(() => {
      render(<Navbar />);
    });
    expect(document.querySelector(".nav")).toBeDefined();
  });
  it("check correctness", () => {
    act(() => {
      render(<Navbar />);
    });
    const elems = document.querySelectorAll(".nav a");

    elems.forEach((elem, index) => {
      expect(elem.textContent).toBe(paths[index].name);
    });
  });
});
