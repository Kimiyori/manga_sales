import React, { useContext } from "react";
import { Context } from "./App";
import styles from "./SourceMainPage.module.css";

export default function Image({ image }) {
  const { source, type, date } = useContext(Context);
  return (
    <div class={styles["image"]}>
      <span>
        <img src={`http://127.0.0.1:8080/${source}/${type}/${date}/${image}`} />
      </span>
    </div>
  );
}
