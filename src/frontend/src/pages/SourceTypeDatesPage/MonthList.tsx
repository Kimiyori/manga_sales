import React from "react";
import DateList from "./DatesList";
import styles from "./DatesList.module.css";

interface ListMonth {
  year: string;
  months_list: {
    [key: string]: number[];
  };
}
export default function MonthsList({ year, months_list }: ListMonth) {
  return (
    <>
      <div className={styles["year"]}>{year}</div>
      <div className={styles["months"]}>
        {Object.entries(months_list).map(([k, v]) => (
          <DateList key={k} year={year} month={k} dates_list={v} />
        ))}
      </div>
    </>
  );
}
