import React from "react";

export default function TitleCreaters({ data, name }: { data: string[]; name: string }) {
  return (
    <>
      <span>{name}:</span>
      {data.map((item, i) => (
        <span key={i}>{item} </span>
      ))}
    </>
  );
}
