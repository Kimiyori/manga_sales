import React from "react";
import styles from "../../../styles/components/_source_block.module.scss";

export default function ItemTypes({ name, types }: { name: string; types: string[] }) {
  return (
    <>
      <div className={styles.source_type}>
        <span>Types: </span>
        {types.map((type, i) => (
          <a key={i} href={`/${name.toLowerCase()}/${type.toLowerCase()}`}>
            <p className={styles.type}>{type}</p>
          </a>
        ))}
      </div>
    </>
  );
}
