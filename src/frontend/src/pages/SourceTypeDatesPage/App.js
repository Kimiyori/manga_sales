import React, { createContext } from "react";
import { useParams } from "react-router-dom";
import YearsList from "./YearList";
import Fetch from "../../components/Fetch";
import styles from "./SourceMainPage.module.css";
import LoadingComponent from "../../components/LoadingComponent/loadingComponent";
export const Context = createContext();

const MainList = ({ data }) => {
  return (
    <>
      <div className={styles["main"]}>
        <h1>Dates</h1>
        <YearsList years_list={data} />
      </div>
    </>
  );
};
const SourceTypeDatesPage = () => {
  let { source } = useParams();
  let { type } = useParams();
  return (
    <Context.Provider value={{source, type}}>
      <Fetch
        uri={`http://127.0.0.1:8080/${source}/${type}/`}
        renderSuccess={MainList} loadingFallback={LoadingComponent}
      />
    </Context.Provider>
  );
};

export default SourceTypeDatesPage;
