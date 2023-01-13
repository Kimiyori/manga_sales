import React from "react";
import styles from "./Source.module.css";

export default function SourceImage({ image }) {
  return (
    <>
      <div className={styles["image"]}>
        <img src={`http://127.0.0.1:8080/${image}`} />
      </div>
    </>
  );
}
