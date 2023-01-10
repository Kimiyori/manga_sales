import React from "react";
import styles from "./SourceMainPage.module.css";
const SourceName = ({name}) => {
  return (
    <>
      <div >
        <h2 className={styles['title']}>{name}</h2>
      </div>
    </>
  );
};

export default SourceName;
