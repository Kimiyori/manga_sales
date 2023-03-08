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
        <SwipeElement text={year} onClick={changeYear} />
        <SwipeElement text={month} onClick={changeMonth} />
        <DatesList month={month} dates_list={dates} onClick={changeDate} />
      </div>
    </>
  );
}
