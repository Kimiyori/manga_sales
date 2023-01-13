import React from "react";
import SourceElement from "./SourceElement";
export default function SourceList({ data = [] }) {
  return (
    <>
      {data.map((source, i) => (
        <SourceElement key={i} source={source} />
      ))}
    </>
  );
}
