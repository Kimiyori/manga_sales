import React from "react";
import styles from "./ItemBlock.module.scss";
import { ImLink } from "react-icons/im";
export default function ItemLink({ link }: { link: string }) {
  return (
    <>
      <div className={styles["link-wrapper"]}>
        <span>Official Website: </span>
        <a href={link}>
          <ImLink />
          link
        </a>
      </div>
    </>
  );
}
