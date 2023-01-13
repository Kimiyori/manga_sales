import React from "react";
import SourceImage from "./SourceImage";
import SourceName from "./SourceName";
import styles from "./Source.module.css";
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
