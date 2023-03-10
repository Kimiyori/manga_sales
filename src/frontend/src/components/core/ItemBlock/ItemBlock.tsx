import React from "react";
import ItemImage from "./ItemImage";
import ItemTitle from "./ItemTitle";
import ItemDescription from "./ItemDescription";
import styles from "../../../styles/components/_source_block.module.scss";
import ItemTypes from "./ItemTypes";

export type ItemData = {
  image: string;
  name: string;
  description: string;
  link: string;
  types: string[];
};

export default function Item({ data }: { data: ItemData }) {
  return (
    <>
      <div className={styles.source}>
        <ItemImage image={data.image} />
        <div className={styles.source_info}>
          <ItemTitle name={data.name} link={data.link} />
          <ItemDescription name={data.description} />
          <ItemTypes name={data.name} types={data.types} />
        </div>
      </div>
    </>
  );
}
