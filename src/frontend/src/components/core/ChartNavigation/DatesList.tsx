import React, { useContext } from "react";
import { ContextType, DateContext } from "../../../pages/ChartstList/Layout";
import styles from "../../../styles/components/_chart_navigation.module.scss";
export default function DatesList({
  dates_list,
  onClick,
}: {
  dates_list: number[];
  onClick: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
}) {
  const { currentDay } = useContext(DateContext) as ContextType;
  return (
    <>
      <div className={styles["dates-nav-days"]}>
        {dates_list.map((date, i) => (
          <button
            className={`${Number(currentDay) == date ? styles["active_button"] : ""} ${styles.button}`}
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
