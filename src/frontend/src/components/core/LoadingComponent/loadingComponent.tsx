import React from "react";
import styles from "./loading.module.css";
const LoadingComponent: () => JSX.Element = () => {
  return (
    <>
      <div className={styles["spin"]}></div>
    </>
  );
};
export default LoadingComponent;
