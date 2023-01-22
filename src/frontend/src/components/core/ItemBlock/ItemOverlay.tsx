import React from "react";
import styles from "./ItemBlock.module.scss";

export default function ItemOverlay({ name, types }: { name: string; types: string[] }) {
  return (
    <>
      <div className={styles["source-type"]}>
        {types.map((type, i) => (
          <a key={i} href={`${name.toLowerCase()}/${type.toLowerCase()}`}>
            <div className={styles["type"]}>{type}</div>
          </a>
        ))}
      </div>
    </>
  );
}
