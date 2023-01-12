import React from "react";
import SourceList from "./SourceList";
import Fetch from "../../components/Fetch";
import styles from "./SourceMainPage.module.css";
import LoadingComponent from "../../components/LoadingComponent/loadingComponent";
const MainList = ({ data }) => {
  return (
    <>
      <div className={styles["main"]}>
        <h1>Sources manga sales</h1>
        <div className={styles["main-list"]}>
          <SourceList source_list={data} />
        </div>
      </div>
    </>
  );
};
const HomePage = () => {
  return (
    <Fetch
      uri={`http://127.0.0.1:8080`}
      renderSuccess={MainList}
      loadingFallback={LoadingComponent}
    />
  );
};

export default HomePage;
