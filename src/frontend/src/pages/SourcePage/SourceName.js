import React from "react";
import styles from "./Source.module.css";
import PropTypes from "prop-types";

export default function SourceName({ name }) {
  return (
    <>
      <div>
        <h2 className={styles["title"]}>{name}</h2>
      </div>
    </>
  );
}
SourceName.propTypes = {
  name: PropTypes.string,
};
