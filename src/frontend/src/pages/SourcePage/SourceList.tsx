import React from "react";
import Item, { ItemData } from "../../components/core/ItemBlock/ItemBlock";

export default function SourceList({ data = [] }: { data: ItemData[] }) {
  return (
    <>
      {data.map((source, i) => (
        <Item key={i} data={source} />
      ))}
    </>
  );
}
