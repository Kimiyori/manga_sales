import React, { useContext } from "react";
import { DateContext, ContextType } from "../../../pages/ChartstList/Layout";
import styles from "../../../styles/components/_chart_navigation.module.scss";
import SwipeElement from "./SwipeBar";
import DatesList from "./DatesList";

export default function ChartNavigation({ year, month, dates }: { year: string; month: string; dates: number[] }) {
  const { changeMonth, changeYear, changeDate } = useContext(DateContext) as ContextType;
  return (
    <>
      <div className={styles["dates_navigator"]}>
        <SwipeElement className={`${styles["arrow_line"]}`} text={year} onClick={changeYear} />
        <SwipeElement className={`${styles["arrow_line"]}`} text={month} onClick={changeMonth} />
        <DatesList dates_list={dates} onClick={changeDate} />
      </div>
    </>
  );
}
