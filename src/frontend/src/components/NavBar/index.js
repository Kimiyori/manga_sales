import React from "react";
import NavList from "./NavList";
import NavIcon from "./NavIcon";
import styles from "./NavBar.module.css";
const Navbar = () => {
  const paths = [
    { path: "/", name: "Home" },
    { path: "about", name: "About" },
    { path: "contact", name: "Contact" },
  ];
  return (
    <>
      <header>
        <nav className={styles["navbar"]}>
          <NavIcon />
          <NavList items={paths} />
        </nav>
      </header>
    </>
  );
};

export default Navbar;
