import React from "react";
import Rating from "./RatingElement";
import Image from "./ImageElement";
import List from "./List";
import styles from "./TitlesList.module.css";

const TitleElement = ({ item }) => {
  return (
    <>
      <div class={styles["item"]}>
        <Rating rating={item.rating} />
        <Image image={item.image} />
        <div class="wrap-text">
          <h2 class="title">{item.title}</h2>
          <List data={item.authors} name="Authors" />
          <List data={item.publishers} name="Publishers" />
          <p>Release:{item.release_date}</p>
          <p>Volume: {item.volume}</p>
          {item.sales && <p>Sales: {item.sales}</p>}
        </div>
      </div>
    </>
  );
};

export default TitleElement;