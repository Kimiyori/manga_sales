import React from "react";
import styles from "./list.module.css";
import PropTypes from "prop-types";
export default function ListWrapper({ title, component }) {
  return (
    <div className={styles["main"]}>
      <h1>{title}</h1>
      <div className={styles["main-list"]}>{component}</div>
    </div>
  );
}

ListWrapper.propTypes = {
  title: PropTypes.string,
  component: PropTypes.element,
};
