import React from "react";
import SourceElement from "./SourceElement";
import styles from "./SourceMainPage.module.css";
const SourceList = ({source_list=[]}) => {

  return (
    <>
      <div className={styles['main-list']}>
          {source_list.map((source,i) => (
            <SourceElement key={i} source={source} />
          ))}
      </div>
    </>
  );
};

export default SourceList;
