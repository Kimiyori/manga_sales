import React from "react";
import styles from "./SourceMainPage.module.css";
const TypeElement = ({ type }) => {
  return (
    <>
      <a href={'/'+type.toLowerCase()}>{type}</a>
    </>
  );
};

export default TypeElement;
