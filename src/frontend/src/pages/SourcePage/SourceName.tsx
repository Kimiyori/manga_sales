import React from "react";
import styles from "./Source.module.css";

export default function SourceName({ name }: { name: string }) {
  return (
    <>
      <div>
        <h2 className={styles["title"]}>{name}</h2>
      </div>
    </>
  );
}
