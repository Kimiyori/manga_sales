import React from "react";
import DateElement from "./DateElement";
import styles from "./DatesList.module.css";
import PropTypes from "prop-types";

export default function DateList({ year, month, dates_list = [] }) {
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
DateList.propTypes = {
  year: PropTypes.string,
  month: PropTypes.string,
  dates_list: PropTypes.arrayOf(PropTypes.number),
};
