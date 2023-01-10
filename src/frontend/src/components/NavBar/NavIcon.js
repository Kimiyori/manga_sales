import { IoAppsSharp } from "react-icons/io5";
import styles from "./NavBar.module.css";
const NavIcon = () => {
  return (
    <>
      <a href="/" className={styles['nav-logo']}>
          <IoAppsSharp />
      </a>
    </>
  );
};

export default NavIcon;
