import React from "react";
import SourceElement from "./SourceElement";
import type { SourceData } from "./SourceElement";
export type SourceProp = {
  data: SourceData[];
};

export default function SourceList({ data = [] }: SourceProp) {
  return (
    <>
      {data.map((source, i) => (
        <SourceElement key={i} source={source} />
      ))}
    </>
  );
}
