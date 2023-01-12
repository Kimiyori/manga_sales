import React, { useContext } from "react";
import { Context } from "./App";
const TypeElement = ({ type }) => {
  const { source } = useContext(Context);
  return (
    <>
      <a href={"/" + source + "/" + type.toLowerCase()}>{type}</a>
    </>
  );
};

export default TypeElement;
