import React from "react";
import SourceElement from "./SourceElement";
import styles from "./SourceMainPage.module.css";
const SourceList = ({ source_list = [] }) => {
  return (
    <>
      {source_list.map((source, i) => (
        <SourceElement key={i} source={source} />
      ))}
    </>
  );
};

export default SourceList;
