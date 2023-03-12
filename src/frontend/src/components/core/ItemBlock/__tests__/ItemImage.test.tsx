import React from "react";
import { act } from "react-dom/test-utils";
import ItemImage from "../ItemImage";
import { render, cleanup } from "@testing-library/react";
import "@testing-library/jest-dom";
afterEach(cleanup);
const data = { name: "test_name", image: "test_url", types: ["test_type"] };
describe("ItemImage", () => {
  it("alt contains correct value", () => {
    act(() => {
      render(<ItemImage {...data} />);
    });
    const testImage = document.querySelector("img") as HTMLImageElement;
    expect(testImage.alt).toContain(data.image);
  });
  it("src contains correct value", () => {
    act(() => {
      render(<ItemImage {...data} />);
    });
    const testImage = document.querySelector("img") as HTMLImageElement;
    expect(testImage.src).toContain(data.image);
  });
});
