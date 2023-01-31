import React from "react";
import styles from "./ChartNavigation.module.scss";

import { AiOutlineArrowLeft, AiOutlineArrowRight } from "react-icons/ai";
export default function SwipeElement({
  className,
  text,
  onClick,
}: {
  className: string;
  text: string;
  onClick?: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
}) {
  return (
    <>
      <div className={className}>
        <div className={styles["left-arrow-button"]}>
          <button data-arrow="left" type="button" onClick={onClick}>
            <AiOutlineArrowLeft />
          </button>
        </div>
        <div className={styles["center-info"]}>{text}</div>
        <div className={styles["right-arrow-button"]}>
          <button data-arrow="right" type="button" onClick={onClick}>
            <AiOutlineArrowRight />
          </button>
        </div>
      </div>
    </>
  );
}
