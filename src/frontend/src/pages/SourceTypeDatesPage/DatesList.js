import React from "react";
import DateElement from "./DateElement";
import styles from "./DatesList.module.css";
export default function DateList({ year, month, dates_list = [] }) {
  return (
    <>
      <div className={styles["month-item"]}>
        <div >{month}</div>
        <div class={styles["date-list"]}>
          {dates_list.map((day, i) => (
            <DateElement key={i} year={year} month={month} day={day} />
          ))}
        </div>
      </div>
    </>
  );
}
