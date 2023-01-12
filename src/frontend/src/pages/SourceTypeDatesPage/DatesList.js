import React from "react";
import DateElement from "./DateElement";
import styles from "./SourceMainPage.module.css";
const DateList = ({ year, month, dates_list = [] }) => {
  return (
    <>
      <div className={styles["month-item"]}>
        <div class={styles["name_month"]}>{month}</div>
        <div class={styles["date-list"]}>
          {dates_list.map((day, i) => (
            <DateElement key={i} year={year} month={month} day={day} />
          ))}
        </div>
      </div>
    </>
  );
};

export default DateList;
