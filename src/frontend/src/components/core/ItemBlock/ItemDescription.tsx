import React from "react";
import styles from "./ItemBlock.module.scss";

export default function ItemDescription({ name = "" }: { name?: string }) {
  return (
    <>
      <div className={styles["description"]}>{name}</div>
    </>
  );
}
