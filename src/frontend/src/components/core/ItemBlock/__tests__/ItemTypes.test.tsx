import React from "react";
import { act } from "react-dom/test-utils";
import { render, cleanup } from "@testing-library/react";
import "@testing-library/jest-dom";
import ItemTypes from "../ItemTypes";
afterEach(cleanup);
const data = { name: "test_name", types: ["test_type", "type2"] };
describe("ItemTypes", () => {
  it("renders without crushing", () => {
    act(() => {
      render(<ItemTypes {...data} />);
    });
    expect(screen).toBeDefined();
  });
  it("renders elements", () => {
    act(() => {
      render(<ItemTypes {...data} />);
    });
    expect(document.querySelector(".source_type")).toBeDefined();
  });
  it("check hrefs", () => {
    act(() => {
      render(<ItemTypes {...data} />);
    });
    const a_tags = document.querySelectorAll(".source_type a");
    a_tags.forEach((elem, index) => {
      expect(elem.href).toBe("http://localhost/test_name/" + data.types[index]);
    });
  });
});
