import React from "react";
import { act } from "react-dom/test-utils";
import ItemImage from "../ItemImage";
import { render, cleanup, fireEvent } from "@testing-library/react";
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
  it("hover", () => {
    act(() => {
      render(<ItemImage {...data} />);
    });
    const testImage = document.querySelector("img") as HTMLImageElement;
    fireEvent.mouseOver(testImage);
    const HoverComponentOver = document.querySelector(".source_type") as HTMLImageElement;
    expect(HoverComponentOver).toBeInTheDocument();
    expect(HoverComponentOver.textContent).toContain(data.types[0]);
    fireEvent.mouseOut(testImage);
    const HoverComponentOut = document.querySelector(".source_type") as HTMLImageElement;
    expect(HoverComponentOut).toBe(null);
  });
});
