import React, { useContext } from "react";
import { Context } from "./App";
import styles from "./DatesList.module.css";
import PropTypes from "prop-types";

function getMonthNumberFromName(monthName) {
  return String(new Date(`${monthName} 1, 2022`).getMonth() + 1).padStart(
    2,
    "0"
  );
}

export default function DateElement({ year, month, day }) {
  const { source } = useContext(Context);
  const { type } = useContext(Context);
  const month_num = getMonthNumberFromName(month);
  return (
    <>
      <div className={styles["date"]}>
        <a
          href={
            "/" +
            source +
            "/" +
            type +
            "/" +
            year +
            "-" +
            month_num +
            "-" +
            String(day).padStart(2, "0")
          }
        >
          {day}
        </a>
      </div>
    </>
  );
}
DateElement.propTypes = {
  year: PropTypes.string,
  month: PropTypes.string,
  day: PropTypes.number,
};
