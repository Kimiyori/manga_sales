import React from "react";
import MonthsList from "./MonthList";
import styles from "./DatesList.module.css";
interface DatesObject {
  [key: string]: {
    [key: string]: number[];
  };
}

function YearElement({ year }: { year: DatesObject }) {
  return (
    <>
      <div className={styles["year-item"]}>
        {Object.keys(year).map((k, i) => (
          <MonthsList key={i} year={k} months_list={year[k]} />
        ))}
      </div>
    </>
  );
}

export default function YearsList({ data }: { data: DatesObject[] }) {
  return (
    <>
      {data.map((year, i) => (
        <YearElement key={i} year={year} />
      ))}
    </>
  );
}
