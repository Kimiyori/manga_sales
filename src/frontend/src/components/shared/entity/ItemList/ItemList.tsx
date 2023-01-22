import React from "react";
import styles from "./list.module.css";

export default function ListWrapper({ component }: { component: React.ReactElement }) {
  return <div className={styles["grid-list"]}>{component}</div>;
}
