import React, { createContext } from "react";
import { useParams } from "react-router-dom";
import TypesList from "./TypesList";
import Fetch from "../../components/Fetch";
import styles from "./SourceMainPage.module.css";
import LoadingComponent from "../../components/LoadingComponent/loadingComponent";
const MainList = ({ data }) => {
  return (
    <>
      <div className={styles["main"]}>
        <h1>Types</h1>
        <TypesList types_list={data} />
      </div>
    </>
  );
};
export const Context = createContext();
const SourceTypePage = () => {
  let { source } = useParams();
  return (
    <Context.Provider value={{ source }}>
      <Fetch
        uri={`http://127.0.0.1:8080/${source}/`}
        renderSuccess={MainList} loadingFallback={LoadingComponent}
      />
    </Context.Provider>
  );
};

export default SourceTypePage;
