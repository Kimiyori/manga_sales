import React from "react";
import styles from "./ItemBlock.module.scss";
import { ImLink } from "react-icons/im";
export default function ItemLink({ link }: { link: string }) {
  return (
    <>
      <div className={styles["link-wrapper"]}>
        <a href={link}>
          <ImLink /> To the site
        </a>
      </div>
    </>
  );
}
