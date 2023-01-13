import React from "react";
import NavElement from "./NavElement";
import styles from "./NavBar.module.css";
import PropTypes from "prop-types";
export default function NavList({ items = [] }) {
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
}

NavList.propTypes = {
  items: PropTypes.arrayOf(
    PropTypes.shape({ name: PropTypes.string, path: PropTypes.string })
  ),
};
