import React, { useContext } from "react";
import { Context } from "./App";
import styles from "./TitlesList.module.css";

export default function Image({ image }: { image: string }) {
  const { source, type, date } = useContext(Context);
  return (
    <div className={styles["image"]}>
      <span>
        <img src={`http://127.0.0.1:8080/${source}/${type}/${date}/${image}`} alt={image} />
      </span>
    </div>
  );
}
