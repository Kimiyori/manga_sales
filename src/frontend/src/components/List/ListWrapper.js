import React from "react";
import SourceList from "./SourceList";
import styles from "./SourceMainPage.module.css";
const MainList = ({ data }) => {
    return (
      <>
        <div className={styles["main"]}>
          <h1>Sources manga sales</h1>
          <SourceList source_list={data} />
        </div>
      </>
    );
  };