import React, { useContext } from "react";
import { Context } from "./App";
export default function TypeElement({ type }) {
  const { source } = useContext(Context);
  return (
    <>
      <a href={"/" + source + "/" + type.toLowerCase()}>{type}</a>
    </>
  );
}
