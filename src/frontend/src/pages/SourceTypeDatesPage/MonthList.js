import React from "react";
import DateList from "./DatesList";
import styles from "./DatesList.module.css";
import PropTypes from "prop-types";

export default function MonthsList({ year, months_list = {} }) {
  return (
    <>
      <div className={styles["year-item"]}>
        <div className={styles["year"]}>{year}</div>
        <div className={styles["months"]}>
          {Object.entries(months_list).map(([k, v]) => (
            <DateList key={k} year={year} month={k} dates_list={v} />
          ))}
        </div>
      </div>
    </>
  );
}
MonthsList.propTypes = {
  year: PropTypes.string,
  months_list: PropTypes.shape({
    year: PropTypes.arrayOf(PropTypes.number),
  }),
};
