import React from "react";
import styles from "./styles.module.scss";
import VerticalInfoBar from "../VerticalInfoBar/VerticalInfoBar";
import TitleCreaters from "./TitleCreaters";
export type TitleData = {
  rating: number;
  image: string;
  title: string;
  authors: string[];
  publishers: string[];
  release_date: string;
  volume: number;
  sales: number | null;
};
export const TitleCard = ({ title_data, date }: { title_data: TitleData; date: string }) => {
  return (
    <>
      <div className={styles["container"]}>
        <div className={styles["title_rating"]}>{title_data.rating}</div>
        <div className={styles["title_image"]}>
          <img src={`${date}/${title_data.image}`} alt={title_data.image} />
        </div>
        <div className={styles["main_info"]}>
          <div className={styles["title_name"]}>
            <h2 className={styles["title"]}>{title_data.title}</h2>
          </div>
          <div className={styles["chart_info"]}>
            <div className={styles["release"]}>
              <VerticalInfoBar title="Release" data={title_data.release_date} />
            </div>
            <div className={styles["volume"]}>
              <VerticalInfoBar title="Volume" data={title_data.volume} />
            </div>
            <div className={styles["sales"]}>
              <VerticalInfoBar title="Sales" data={title_data.sales ? title_data.sales : "N/A"} />
            </div>
          </div>
          <div className={styles["creators"]}>
            <div className={styles["authors_list"]}>
              <TitleCreaters data={title_data.authors} name="Authors" />
            </div>
            <div className={styles["publishers_list"]}>
              <TitleCreaters data={title_data.publishers} name="Publishers" />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};