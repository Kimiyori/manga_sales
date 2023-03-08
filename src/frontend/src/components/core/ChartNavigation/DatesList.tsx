import React, { useContext } from "react";
import { ContextType, DateContext } from "../../../pages/ChartstList/Layout";
import styles from "../../../styles/components/_chart_navigation.module.scss";
export default function DatesList({
  month,
  dates_list,
  onClick,
}: {
  month: string;
  dates_list: number[];
  onClick: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
}) {
  const { currentDay, currentDate } = useContext(DateContext) as ContextType;
  const currentMonth = new Date(currentDate).toLocaleString("en-us", { month: "long" });
  return (
    <>
      <div className={styles["dates-nav-days"]}>
        {dates_list.map((date, i) => (
          <button
            className={`${month == currentMonth && Number(currentDay) == date ? styles["active_button"] : ""} ${
              styles.button
            }`}
            key={i}
            onClick={onClick}
          >
            {date}
          </button>
        ))}
      </div>
    </>
  );
}
