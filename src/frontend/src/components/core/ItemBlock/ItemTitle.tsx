import React from "react";
import styles from "./ItemBlock.module.scss";

export default function ItemTitle({ name = "" }: { name?: string }) {
  return (
    <>
      <div className={styles["title"]}>{name}</div>
    </>
  );
}
