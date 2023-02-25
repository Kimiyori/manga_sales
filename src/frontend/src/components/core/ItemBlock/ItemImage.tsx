import React, { useState } from "react";
import ItemOverlay from "./ItemOverlay";
import styles from "../../../styles/components/_source_block.module.scss";
import ImageLoad from "../../../hooks/ImageLoad";
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
      <div onMouseOver={handleMouseOver} onMouseOut={handleMouseOut} className={styles.image}>
        <ImageLoad src={`/api/${image}`} alt={image} style={{ opacity: isHovering ? 0.7 : 1 }} />
        {isHovering && <ItemOverlay name={name} types={types} />}
      </div>
    </>
  );
}
