import React from "react";
import styles from "../../../styles/components/_source_block.module.scss";
import ImageLoad from "../../../hooks/ImageLoad";
export default function ItemImage({ image }: { image: string }) {
  return (
    <>
      <div className={styles.image}>
        <ImageLoad src={`${process.env.REACT_APP_BACKEND_URL}/${image}`} alt={image} />
      </div>
    </>
  );
}
