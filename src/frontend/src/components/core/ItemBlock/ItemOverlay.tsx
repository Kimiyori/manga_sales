import React from "react";
import styles from "../../../styles/components/_source_block.module.scss";

export default function dItemOverlay({ name, types }: { name: string; types: string[] }) {
  return (
    <>
      <div className={styles.source_type}>
        {types.map((type, i) => (
          <a key={i} href={`${name.toLowerCase()}/${type.toLowerCase()}`}>
            <div className={styles.type}>{type}</div>
          </a>
        ))}
      </div>
    </>
  );
}
