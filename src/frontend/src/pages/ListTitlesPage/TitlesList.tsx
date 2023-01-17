import React from "react";
import TitleElement from "./ItemElement";

export type DataList = {
  rating: number;
  image: string;
  title: string;
  authors: string[];
  publishers: string[];
  release_date: string;
  volume: number;
  sales: number | null;
};
export default function TitlesList({ data }: { data: DataList[] }) {
  return (
    <>
      {data.map((item, i) => (
        <TitleElement key={i} item={item} />
      ))}
    </>
  );
}
