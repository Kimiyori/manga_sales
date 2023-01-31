import React from "react";
import styles from "./ChartNavigation.module.scss";
import SwipeElement from "./SwipeBar";
import DatesList from "./DatesList";

export default function ChartNavigation({
  year,
  month,
  dates,
  changeYear,
  changeMonth,
  changeData,
}: {
  year: string;
  month: string;
  dates: number[];
  changeYear: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  changeMonth: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  changeData: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
}) {
  return (
    <>
      <div className={styles["dates_navigator"]}>
        <SwipeElement className={styles["dates-nav-year"]} text={year} onClick={changeYear} />
        <SwipeElement className={styles["dates-nav-month"]} text={month} onClick={changeMonth} />
        <DatesList dates_list={dates} onClick={changeData} />
        <div className={styles["right-nav"]}></div>
        <div className={styles["right-nav-bottom"]}></div>
      </div>
    </>
  );
}
