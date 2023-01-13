import React from "react";
export default function List({ data,name }) {
  return (
    <>
      <p> {name}: 
       {data.map((item) => ( item ))}
      </p>
    </>
  );
}
