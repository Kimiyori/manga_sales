import React from "react";
import ChartNavigation from "../ChartNavigation";
import { render, cleanup, screen, fireEvent } from "@testing-library/react";
import { createRandomYearList } from "./fakeData";

afterEach(cleanup);

describe("ChartNavigation", () => {
  const fakeData = createRandomYearList(5);
  it("renders without crushing", () => {
    render(<ChartNavigation data={fakeData} />);
    expect(screen).toBeDefined();
  });
  it("checking child elements", () => {
    const { container } = render(<ChartNavigation data={fakeData} />);
    expect(container).toBeDefined();
    expect(container.querySelector(".dates-nav-year")).toBeDefined();
    expect(container.querySelector(".dates-nav-month")).toBeDefined();
    expect(container.querySelector(".dates-nav-days")).toBeDefined();
    expect(container.querySelector(".right-nav")).toBeDefined();
    expect(container.querySelector(".right-nav-bottom")).toBeDefined();
  });
  it("check correct year at the beginning", () => {
    const { container } = render(<ChartNavigation data={fakeData} />);
    expect(container.querySelector(".dates-nav-year")?.textContent).toBe(fakeData.at(-1)?.year);
  });
  it("check correct month at the beginning", () => {
    const { container } = render(<ChartNavigation data={fakeData} />);
    expect(container.querySelector(".dates-nav-month")?.textContent).toBe(fakeData.at(-1)?.months.at(-1)?.name);
  });
  it("check dates list", () => {
    const { container } = render(<ChartNavigation data={fakeData} />);
    expect(container.querySelector(".dates-nav-days")?.textContent).toBe(
      fakeData.at(-1)?.months.at(-1)?.dates.join("")
    );
  });
  it("get previous year", () => {
    const { container } = render(<ChartNavigation data={fakeData} />);
    const left_button = container.querySelector(".dates-nav-year .left-arrow-button button") as HTMLElement;
    fireEvent.click(left_button);
    expect(container.querySelector(".dates-nav-year")?.textContent).toBe(fakeData.at(-2)?.year);
    expect(container.querySelector(".dates-nav-month")?.textContent).toBe(fakeData.at(-2)?.months.at(-1)?.name);
    expect(container.querySelector(".dates-nav-days")?.textContent).toBe(
      fakeData.at(-2)?.months.at(-1)?.dates.join("")
    );
  });
  it("get previous year if alrealy last", () => {
    const { container } = render(<ChartNavigation data={fakeData} />);
    const left_button = container.querySelector(".dates-nav-year .left-arrow-button button") as HTMLElement;
    for (let i = 0; i < 7; i++) fireEvent.click(left_button);
    expect(container.querySelector(".dates-nav-year")?.textContent).toBe(fakeData.at(0)?.year);
    expect(container.querySelector(".dates-nav-month")?.textContent).toBe(fakeData.at(0)?.months.at(0)?.name);
  });
  it("get next year if it not last", () => {
    const { container } = render(<ChartNavigation data={fakeData} />);
    const left_button = container.querySelector(".dates-nav-year .left-arrow-button button") as HTMLElement;
    fireEvent.click(left_button);
    fireEvent.click(left_button);
    const right_button = container.querySelector(".dates-nav-year .right-arrow-button button") as HTMLElement;
    fireEvent.click(right_button);
    expect(container.querySelector(".dates-nav-year")?.textContent).toBe(fakeData.at(-2)?.year);
    expect(container.querySelector(".dates-nav-month")?.textContent).toBe(fakeData.at(-2)?.months.at(0)?.name);
    expect(container.querySelector(".dates-nav-days")?.textContent).toBe(fakeData.at(-2)?.months.at(0)?.dates.join(""));
  });
  it("get next year if its already last", () => {
    const { container } = render(<ChartNavigation data={fakeData} />);
    const right_button = container.querySelector(".dates-nav-year .right-arrow-button button") as HTMLElement;
    fireEvent.click(right_button);
    expect(container.querySelector(".dates-nav-year")?.textContent).toBe(fakeData.at(-1)?.year);
    expect(container.querySelector(".dates-nav-month")?.textContent).toBe(fakeData.at(-1)?.months.at(-1)?.name);
  });
});
