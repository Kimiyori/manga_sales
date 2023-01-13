import React from "react";
import DateList from "./DatesList";
import styles from "./DatesList.module.css";
export default function MonthsList({ year, months_list = {} }) {
  return (
    <>
      <div class={styles["year-item"]}>
        <div class={styles["year"]}>{year}</div>
        <div class={styles["months"]}>
          {Object.entries(months_list).map(([k, v]) => (
            <DateList key={k} year={year} month={k} dates_list={v} />
          ))}
        </div>
      </div>
    </>
  );
}
