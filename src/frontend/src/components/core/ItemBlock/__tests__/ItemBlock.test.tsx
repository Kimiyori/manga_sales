import React from "react";
import { act } from "react-dom/test-utils";
import Item from "../ItemBlock";
import { render, cleanup, screen } from "@testing-library/react";

afterEach(cleanup);
const data_item = {
  name: "Oricon",
  image: "oricon/logo.png",
  description: `Oricon is the holding company at the head of a Japanese corporate group that monitors and reports 
    on sales of CDs, DVDs, video games,and entertainment content in several other formats; 
    manga and book sales were also formerly covered.`,
  link: "https://www.oricon.co.jp",
  types: ["Weekly"],
};

describe("ItemBlock", () => {
  it("renders without crushing", () => {
    act(() => {
      render(<Item data={data_item} />);
    });
    expect(screen).toBeDefined();
  });
  it("renders elements", () => {
    act(() => {
      render(<Item data={data_item} />);
    });
    expect(document.querySelector(".image")).toBeDefined();
    expect(document.querySelector(".title")).toBeDefined();
    expect(document.querySelector(".description")).toBeDefined();
    expect(document.querySelector(".source_type")).toBeDefined();
  });
});
