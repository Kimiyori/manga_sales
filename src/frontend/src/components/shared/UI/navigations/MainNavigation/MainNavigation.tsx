import React from "react";
import "../../../../../styles/components/_navigation.scss";
import NavElement from "./NavElement";
export const paths = [
  { path: "/source", name: "Source" },
  { path: "/about", name: "About" },
  { path: "/contact", name: "Contact" },
];
export default function Navbar() {
  return (
    <>
      <nav className={"nav"}>
        <ul>
          {paths.map((item, i) => (
            <NavElement key={i} title={item.name} path={item.path} />
          ))}
        </ul>
      </nav>
    </>
  );
}
