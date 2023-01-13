import React from "react";
import PropTypes from "prop-types";
export default function List({ data, name }) {
  return (
    <>
      <p>
        {" "}
        {name}:{data.map((item) => item)}
      </p>
    </>
  );
}

List.propTypes = {
  data: PropTypes.arrayOf(PropTypes.string),
  name: PropTypes.stirng,
};
