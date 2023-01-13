import React, { useContext } from "react";
import styles from "./TitlesList.module.css";

const Rating = ({ rating }) => {
  return (
    <>
      <div class={styles["rating"]}>
        <h1>{ rating }</h1>
      </div>
    </>
  );
};

export default Rating;
