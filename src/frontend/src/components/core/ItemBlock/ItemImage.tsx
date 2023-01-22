import React, { useState } from "react";
import ItemOverlay from "./ItemOverlay";
import styles from "./ItemBlock.module.scss";

export default function ItemImage({ name, image, types }: { name: string; image: string; types: string[] }) {
  const [isHovering, setIsHovering] = useState(false);
  const handleMouseOver = () => {
    setIsHovering(true);
  };

  const handleMouseOut = () => {
    setIsHovering(false);
  };
  return (
    <>
      <div onMouseOver={handleMouseOver} onMouseOut={handleMouseOut} className={styles["image"]}>
        <img style={{ opacity: isHovering ? 0.7 : 1 }} src={`http://127.0.0.1:8080/${image}`} alt={image} />
        {isHovering && <ItemOverlay name={name} types={types} />}
      </div>
    </>
  );
}
