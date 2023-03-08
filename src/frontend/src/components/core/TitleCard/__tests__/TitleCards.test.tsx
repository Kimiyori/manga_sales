import React from "react";
import { act } from "react-dom/test-utils";
import { render, cleanup, screen } from "@testing-library/react";
import { TitleCard } from "../TitleCard";
import fakeData from "./fakeData";

afterEach(cleanup);

describe("ItemBlock", () => {
  it("renders without crushing", () => {
    act(() => {
      render(<TitleCard title_data={fakeData} date={"2022-03-03"} />);
    });
    expect(screen).toBeDefined();
  });
  it("renders elements", () => {
    act(() => {
      render(<TitleCard title_data={fakeData} date={"2022-03-03"} />);
    });
    expect(document.querySelector(".container")).toBeDefined();
    expect(document.querySelector(".title_image")).toBeDefined();
    expect(document.querySelector(".title_rating")).toBeDefined();
    expect(document.querySelector(".title_prev_rank")).toBeDefined();
    expect(document.querySelector(".main_info")).toBeDefined();
  });
  it("render prev_rank", () => {
    act(() => {
      render(<TitleCard title_data={fakeData} date={"2022-03-03"} />);
    });
    expect(document.querySelector(".title_prev_rank")).toBeDefined();
    expect(document.querySelector(".title_prev_rank svg")?.style.color).toBe("rgb(26, 211, 26)");
  });
});
