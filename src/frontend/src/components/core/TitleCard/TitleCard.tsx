import React from "react";
import styles from "./styles.module.scss";
import VerticalInfoBar from "../VerticalInfoBar/VerticalInfoBar";
import TitleCreaters from "./TitleCreaters";
import { SourceContextType } from "../../../pages/ChartstList";
import { useParams } from "react-router-dom";
import { BsFillArrowUpSquareFill, BsFillArrowDownSquareFill } from "react-icons/bs";
import ImageLoad from "../ImageLoad/ImageLoad";

export type TitleData = {
  rating: number;
  image: string;
  title: string;
  authors: string[];
  publishers: string[];
  release_date: string;
  volume: number;
  sales: number | null;
  prev_rank: string | null;
};
export const TitleCard = ({ title_data, date }: { title_data: TitleData; date: string }) => {
  const { source, type } = useParams<SourceContextType>();
  return (
    <>
      <div className={styles["container"]}>
        <div className={styles["title_image"]}>
          <ImageLoad
            src={`http://127.0.0.1:8080/${source}/${type}/${date}/${title_data.image}`}
            alt={title_data.image}
          />
          <div className={styles["title_rating"]}>{title_data.rating}</div>
          {title_data.prev_rank && (
            <div className={styles["title_prev_rank"]}>
              {title_data.prev_rank == "UP" ? (
                <BsFillArrowUpSquareFill style={{ color: "#1ad31a" }} />
              ) : (
                <BsFillArrowDownSquareFill style={{ color: "rgb(237 14 14)" }} />
              )}
            </div>
          )}
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
