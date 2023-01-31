import React from "react";
import styles from "./loading.module.css";
const LoadingComponent: React.FunctionComponent = () => {
  return (
    <>
      <div className={styles["spin"]}></div>
    </>
  );
};
export default LoadingComponent;
