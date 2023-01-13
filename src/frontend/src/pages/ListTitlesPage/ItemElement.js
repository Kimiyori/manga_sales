import React from "react";
import Rating from "./RatingElement";
import Image from "./ImageElement";
import List from "./List";
import styles from "./TitlesList.module.css";
import PropTypes from "prop-types";

export default function TitleElement({ item }) {
  return (
    <>
      <div className={styles["item"]}>
        <Rating rating={item.rating} />
        <Image image={item.image} />
        <div className="wrap-text">
          <h2 className="title">{item.title}</h2>
          <List data={item.authors} name="Authors" />
          <List data={item.publishers} name="Publishers" />
          <p>Release:{item.release_date}</p>
          <p>Volume: {item.volume}</p>
          {item.sales && <p>Sales: {item.sales}</p>}
        </div>
      </div>
    </>
  );
}

TitleElement.propTypes = {
  item: PropTypes.shape({
    rating: PropTypes.number,
    image: PropTypes.string,
    title: PropTypes.string,
    authors: PropTypes.arrayOf(PropTypes.string),
    publishers: PropTypes.arrayOf(PropTypes.string),
    release_date: PropTypes.string,
    volume: PropTypes.number,
    sales: PropTypes.number,
  }),
};
