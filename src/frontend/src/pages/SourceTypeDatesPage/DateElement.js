import React, { useContext } from "react";
import { Context } from "./App";
import styles from "./SourceMainPage.module.css";
function getMonthNumberFromName(monthName) {
  return String(new Date(`${monthName} 1, 2022`).getMonth() + 1).padStart(
    2,
    "0"
  );
}
const DateElement = ({ year, month, day }) => {
  const { source } = useContext(Context);
  const { type } = useContext(Context);
  const month_num = getMonthNumberFromName(month);
  return (
    <>
      <div class={styles["date"]}>
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
};

export default DateElement;
