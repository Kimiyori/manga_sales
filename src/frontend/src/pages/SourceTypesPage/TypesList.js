import React from "react";
import TypeElement from './Type'
import styles from "./SourceMainPage.module.css";
const TypesList = ({types_list=[]}) => {

  return (
    <>
      <div className={styles['main-list']}>
          {types_list.map((source,i) => (
            <TypeElement key={i} type={source.type} />
          ))}
      </div>
    </>
  );
};

export default TypesList;