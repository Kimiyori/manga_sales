import React from "react";
import MonthsList from "./MonthList";
export default function YearsList({ data = {} }) {
  return (
    <>
      {data.map((year, i) =>
        Object.keys(year).map((k, v) => (
          <MonthsList key={k} year={k} months_list={year[k]} />
        ))
      )}
    </>
  );
}
