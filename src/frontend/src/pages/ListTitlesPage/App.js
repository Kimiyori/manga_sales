import React, { createContext } from "react";
import { useParams } from "react-router-dom";
import Fetch from "../../components/Fetch";
import styles from "./SourceMainPage.module.css";
import LoadingComponent from "../../components/LoadingComponent/loadingComponent";
import TitlesList from "./TitlesList";
export const Context = createContext();

const TitlesListMain = () => {
  let { source, type, date } = useParams();
  return (
    <>
      <div className={styles["main"]}>
        <div className={styles["main-list"]}>
          <Context.Provider value={{ source, type, date }}>
            <Fetch
              uri={`http://127.0.0.1:8080/${source}/${type}/${date}/`}
              renderSuccess={TitlesList}
              loadingFallback={LoadingComponent}
            />
          </Context.Provider>
        </div>
      </div>
    </>
  );
};

export default TitlesListMain;
