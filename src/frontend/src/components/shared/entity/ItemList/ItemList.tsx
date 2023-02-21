import React from "react";
import styles from "../../../../styles/components/_list_wrapper.module.scss";

export default function ListWrapper({ component }: { component: React.ReactElement }) {
  return <div className={styles["grid-list"]}>{component}</div>;
}
