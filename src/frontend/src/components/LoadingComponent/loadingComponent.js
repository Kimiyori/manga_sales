import React from "react";
import styles from "./loading.css";
export default function LoadingComponent() {
  return (
    <>
      <div className={styles["spin"]}></div>
    </>
  );
}
