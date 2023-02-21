import React from "react";
import styles from "../../../styles/components/_source_block.module.scss";

export default function ItemTitle({ name = "" }: { name?: string }) {
  return (
    <>
      <div className={styles["title"]}>{name}</div>
    </>
  );
}
