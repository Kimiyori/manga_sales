import React from "react";
import PropTypes from "prop-types";

export default function NavElement({ title, path }) {
  return (
    <>
      <li>
        <a href={path}>{title}</a>
      </li>
    </>
  );
}

NavElement.propTypes = {
  title: PropTypes.string,
  path: PropTypes.string,
};
