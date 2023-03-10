import React, { useContext } from "react";
import ChartNavigation from "../../components/core/ChartNavigation/ChartNavigation";
import styles from "../../styles/pages/ChartList.module.scss";
import { DatesObject, SourceContextType } from ".";
import { DatesState } from "../../hooks/DateSwipe";
import { ContextType, DateContext } from "./Layout";
import { useParams } from "react-router-dom";

export function UpperBox({ data, date }: { data: DatesObject[]; date: DatesState }) {
  const { setTab } = useContext(DateContext) as ContextType;
  const { source, type } = useParams<SourceContextType>();
  return (
    <>
      <div className={styles.upper_box}>
        <ChartNavigation
          year={data[date.year_index]["year"]}
          month={data[date.year_index]["months"][date.month_index].name}
          dates={data[date.year_index]["months"][date.month_index]["dates"]}
        />
        <div className={styles.base_menu_info}>
          <div className={styles.name}>
            Source: {source} Type:{type}
          </div>
          <button className={styles.tab_button} onClick={() => setTab({ name: "stat" })}>
            Statistics
          </button>
          <button className={styles.tab_button2} onClick={() => setTab({ name: "summary" })}>
            Summary
          </button>
        </div>
      </div>
    </>
  );
}
