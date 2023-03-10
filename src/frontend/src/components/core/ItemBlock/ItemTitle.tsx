import React from "react";
import { ImLink } from "react-icons/im";
import styles from "../../../styles/components/_source_block.module.scss";

export default function ItemTitle({ name, link }: { name: string; link: string }) {
  return (
    <>
      <div className={styles.upper}>
        <div className={styles.title}>{name}</div>
        <div className={styles.link}>
          <a href={link}>
            <ImLink />
            <span> Official Website</span>
          </a>
        </div>
      </div>
    </>
  );
}
