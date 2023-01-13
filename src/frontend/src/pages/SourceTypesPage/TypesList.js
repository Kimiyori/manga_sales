import React from "react";
import TypeElement from "./Type";
import PropTypes from "prop-types";
export default function TypesList({ data = [] }) {
  return (
    <>
      {data.map((source, i) => (
        <TypeElement key={i} type={source.type} />
      ))}
    </>
  );
}
TypesList.propTypes = {
  data: PropTypes.arrayOf(PropTypes.string),
};
