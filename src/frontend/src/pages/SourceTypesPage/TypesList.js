import React from "react";
import TypeElement from "./Type";

export default function TypesList({ data = [] }) {
  return (
    <>
      {data.map((source, i) => (
        <TypeElement key={i} type={source.type} />
      ))}
    </>
  );
}
