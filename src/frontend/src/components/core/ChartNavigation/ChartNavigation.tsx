import React, { useContext } from "react";
import { DateContext, ContextType } from "../../../pages/ChartstList/Layout";
import styles from "./ChartNavigation.module.scss";
import SwipeElement from "./SwipeBar";
import DatesList from "./DatesList";

export default function ChartNavigation({ year, month, dates }: { year: string; month: string; dates: number[] }) {
  const { changeMonth, changeYear, changeDate } = useContext(DateContext) as ContextType;
  return (
    <>
      <div className={styles["dates_navigator"]}>
        <SwipeElement className={styles["dates-nav-year"]} text={year} onClick={changeYear} />
        <SwipeElement className={styles["dates-nav-month"]} text={month} onClick={changeMonth} />
        <DatesList dates_list={dates} onClick={changeDate} />
        <div className={styles["right-nav"]}></div>
        <div className={styles["right-nav-bottom"]}></div>
      </div>
    </>
  );
}
