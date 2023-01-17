import React from "react";

export default function List({ data, name }: { data: string[]; name: string }) {
  return (
    <>
      <p>
        {" "}
        {name}:{data.map((item) => item)}
      </p>
    </>
  );
}
