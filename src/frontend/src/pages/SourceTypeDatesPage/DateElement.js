import React from "react";
import styles from "./SourceMainPage.module.css";
const DateElement = ({ date }) => {
  return (
    <>
      <div class={styles["date"]}>
        <a href="#">{date}</a>
      </div>
    </>
  );
};

export default DateElement;
