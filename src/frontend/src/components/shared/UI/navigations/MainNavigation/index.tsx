import React from "react";
import NavList from "./NavList";
import styles from "./NavBar.module.scss";

export default function Navbar() {
  const paths = [
    { path: "manga", name: "Manga" },
    { path: "about", name: "About" },
    { path: "contact", name: "Contact" },
  ];

  return (
    <>
      <nav className={styles["nav"]}>
        <NavList items={paths} />
      </nav>
    </>
  );
}
