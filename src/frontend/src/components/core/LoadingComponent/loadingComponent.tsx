import React from "react";
import styles from "../../../styles/components/_loading_component.module.scss";
const LoadingComponent: () => JSX.Element = () => {
  return (
    <>
      <div className={styles["spin"]}></div>
    </>
  );
};
export default LoadingComponent;
