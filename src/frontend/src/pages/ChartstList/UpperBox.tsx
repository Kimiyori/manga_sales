import React from "react";
import ChartNavigation from "../../components/core/ChartNavigation/ChartNavigation";
import styles from "../../styles/pages/ChartList.module.scss";
import { DatesObject } from ".";
import { DatesState } from "../../hooks/DateSwipe";

export function UpperBox({ data, date }: { data: DatesObject[]; date: DatesState }) {
  return (
    <>
      <ChartNavigation
        year={data[date.year_index]["year"]}
        month={data[date.year_index]["months"][date.month_index].name}
        dates={data[date.year_index]["months"][date.month_index]["dates"]}
      />
      <div className={styles.base_menu_info}></div>
    </>
  );
}
