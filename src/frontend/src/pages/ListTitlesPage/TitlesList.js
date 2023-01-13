import React from "react";
import PropTypes from "prop-types";
import TitleElement from "./ItemElement";
export default function TitlesList({ data }) {
  return (
    <>
      {data.map((item, i) => (
        <TitleElement key={i} item={item} />
      ))}
    </>
  );
}

TitlesList.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      rating: PropTypes.number,
      image: PropTypes.string,
      title: PropTypes.string,
      authors: PropTypes.arrayOf(PropTypes.string),
      publishers: PropTypes.arrayOf(PropTypes.string),
      release_date: PropTypes.string,
      volume: PropTypes.number,
      sales: PropTypes.number,
    })
  ),
};
