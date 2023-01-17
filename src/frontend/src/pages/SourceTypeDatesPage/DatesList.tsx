import React from "react";
import DateElement from "./DateElement";
import styles from "./DatesList.module.css";

import type { DateNumber } from "./DateElement";

export interface MonthElement {
  month: string;
  dates_list: DateNumber[];
}

interface ListDate extends MonthElement {
  year: string;
}

export default function DateList({ year, month, dates_list = [] }: ListDate) {
  return (
    <>
      <div className={styles["month-item"]}>
        <div>{month}</div>
        <div className={styles["date-list"]}>
          {dates_list.map((day, i) => (
            <DateElement key={i} year={year} month={month} day={day} />
          ))}
        </div>
      </div>
    </>
  );
}
