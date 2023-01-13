import React from "react";

import TitleElement from "./ItemElement";
const TitlesList = ({ data }) => {
  return (
    <>
      {data.map((item, i) => (
        <TitleElement key={i} item={item} />
      ))}
    </>
  );
};

export default TitlesList;
