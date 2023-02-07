import React from "react";
import styles from "./NavBar.module.scss";
import NavElement from "./NavElement";
const paths = [
  { path: "/manga", name: "Manga" },
  { path: "/about", name: "About" },
  { path: "/contact", name: "Contact" },
];
export default function Navbar() {
  return (
    <>
      <nav className={styles["nav"]}>
        <ul>
          {paths.map((item, i) => (
            <NavElement key={i} title={item.name} path={item.path} />
          ))}
        </ul>
      </nav>
    </>
  );
}
