import React, { useContext } from "react";
import { Context } from "./App";
import styles from "./DatesList.module.css";

export type DateNumber = number;

export type Date = {
  year: string;
  month: string;
  day: DateNumber;
};

function getMonthNumberFromName(monthName: string): string {
  return String(new Date(`${monthName} 1, 2022`).getMonth() + 1).padStart(
    2,
    "0"
  );
}

export default function DateElement({ year, month, day }: Date) {
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
