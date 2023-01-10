import React from "react";

const NavElement = ({title, path}) => {
  return (
    <>
      <li>
        <a href={path}>{title}</a>
      </li>
    </>
  );
};

export default NavElement;
