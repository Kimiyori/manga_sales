import React from "react";
import styles from "./ChartNavigation.module.scss";
export default function DatesList({
  dates_list,
  onClick,
}: {
  dates_list: number[];
  onClick: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
}) {
  return (
    <>
      <div className={styles["dates-nav-days"]}>
        {dates_list.map((date, i) => (
          <button key={i} onClick={onClick}>
            {date}
          </button>
        ))}
      </div>
    </>
  );
}
