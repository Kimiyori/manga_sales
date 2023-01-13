import React from "react";
import SourceImage from "./SourceImage";
import SourceName from "./SourceName";
import styles from "./Source.module.css";
import PropTypes from "prop-types";
export default function SourceElement({ source }) {
  return (
    <>
      <a href={"/" + source.name.toLowerCase()}>
        <div className={styles["item"]}>
          <SourceImage image={source.image} />
          <SourceName name={source.name} />
        </div>
      </a>
    </>
  );
}
SourceElement.propTypes = {
  source: PropTypes.shape({
    image: PropTypes.string,
    name: PropTypes.string,
  }),
};
