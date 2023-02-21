import React, { useReducer } from "react";
import styles from "../../../styles/components/_source_block.module.scss";
import { BiCaretDown, BiCaretUp } from "react-icons/bi";
export default function ItemDescription({ name = "" }: { name?: string }) {
  const [checked, toggle] = useReducer((checked) => !checked, true);
  return (
    <>
      <div className={styles["description"]}>
        <p style={{ display: checked ? "-webkit-box" : "block" }} className={styles["description__text"]}>
          {name}
        </p>
        <div>
          <button onClick={toggle}>{checked ? <BiCaretDown /> : <BiCaretUp />}</button>
        </div>
      </div>
    </>
  );
}
