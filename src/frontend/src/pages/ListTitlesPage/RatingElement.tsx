import React from "react";
import styles from "./TitlesList.module.css";

export default function Rating({ rating }: { rating: number }) {
  return (
    <>
      <div className={styles["rating"]}>
        <h1>{rating}</h1>
      </div>
    </>
  );
}
