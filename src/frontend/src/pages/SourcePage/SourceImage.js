import React from "react";
import styles from "./Source.module.css";
import PropTypes from "prop-types";
export default function SourceImage({ image }) {
  return (
    <>
      <div className={styles["image"]}>
        <img src={`http://127.0.0.1:8080/${image}`} alt={image} />
      </div>
    </>
  );
}
SourceImage.propTypes = {
  image: PropTypes.string,
};
