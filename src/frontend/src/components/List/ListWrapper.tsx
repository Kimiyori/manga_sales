import React from "react";
import styles from "./list.module.css";

export default function ListWrapper({
  title,
  component,
}: {
  title: string;
  component: React.ReactElement;
}) {
  return (
    <div className={styles["main"]}>
      <h1>{title}</h1>
      <div className={styles["main-list"]}>{component}</div>
    </div>
  );
}
