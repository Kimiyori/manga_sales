import React from "react";
import ItemImage from "./ItemImage";
import ItemTitle from "./ItemTitle";
import ItemDescription from "./ItemDescription";
import ItemLink from "./ItemLink";
import styles from "./ItemBlock.module.scss";

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
      <div className={styles["wide-items-list"]}>
        <ItemImage image={data.image} name={data.name} types={data.types} />
        <ItemTitle name={data.name} />
        <ItemDescription name={data.description} />
        <ItemLink link={data.link} />
      </div>
    </>
  );
}