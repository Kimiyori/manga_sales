import React from "react";
import NavElement from "./NavElement";
import styles from "./NavBar.module.css";
const NavList = ({ items = [] }) => {
  return (
    <>
      <div className={styles["nav"]}>
        <ul className={styles["nav-links"]}>
          {items.map((item, i) => (
            <NavElement key={i} title={item.name} path={item.path} />
          ))}
        </ul>
      </div>
    </>
  );
};

export default NavList;
