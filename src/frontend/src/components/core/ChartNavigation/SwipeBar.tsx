import React from "react";
import styles from "../../../styles/components/_chart_navigation.module.scss";

import { AiOutlineArrowLeft, AiOutlineArrowRight } from "react-icons/ai";
export default function SwipeElement({
  text,
  onClick,
}: {
  text: string;
  onClick?: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
}) {
  return (
    <>
      <div className={styles["arrow_line"]}>
        <button className={styles["button"]} data-arrow="left" type="button" onClick={onClick}>
          <AiOutlineArrowLeft />
        </button>
        <div className={styles["center-info"]}>{text}</div>
        <button className={styles["button"]} data-arrow="right" type="button" onClick={onClick}>
          <AiOutlineArrowRight />
        </button>
      </div>
    </>
  );
}
