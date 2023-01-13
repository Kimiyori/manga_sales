import React, { useContext } from "react";
import { Context } from "./App";
import PropTypes from "prop-types";
export default function TypeElement({ type }) {
  const { source } = useContext(Context);
  return (
    <>
      <a href={"/" + source + "/" + type.toLowerCase()}>{type}</a>
    </>
  );
}
TypeElement.propTypes = {
  type: PropTypes.string,
};
