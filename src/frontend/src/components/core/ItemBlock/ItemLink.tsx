import React from "react";
import styles from "../../../styles/components/_source_block.module.scss";
import { ImLink } from "react-icons/im";
export default function ItemLink({ link }: { link: string }) {
  return (
    <>
      <div className={styles["link-wrapper"]}>
        <a href={link}>
          <ImLink />
          <span> Official Website</span>
        </a>
      </div>
    </>
  );
}
