import React from "react";
import MonthsList from "./MonthList";
import styles from "./SourceMainPage.module.css";
const YearsList = ({ years_list = {} }) => {
  return (
    <>
      <div className={styles["main-list"]}>
        {years_list.map((year, i) =>
          Object.keys(year).map((k, v) => (
            <MonthsList key={k} year={k} months_list={year[k]} />
          ))
        )}
      </div>
    </>
  );
};

export default YearsList;
