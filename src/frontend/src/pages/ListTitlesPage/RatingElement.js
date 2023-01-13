import React from "react";
import styles from "./TitlesList.module.css";
import PropTypes from "prop-types";

export default function Rating({ rating }) {
  return (
    <>
      <div className={styles["rating"]}>
        <h1>{rating}</h1>
      </div>
    </>
  );
}

Rating.propTypes = {
  rating: PropTypes.number,
};
