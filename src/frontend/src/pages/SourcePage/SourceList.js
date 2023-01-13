import React from "react";
import SourceElement from "./SourceElement";
import PropTypes from "prop-types";
export default function SourceList({ data = [] }) {
  return (
    <>
      {data.map((source, i) => (
        <SourceElement key={i} source={source} />
      ))}
    </>
  );
}
SourceList.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      image: PropTypes.string,
      name: PropTypes.string,
    })
  ),
};
