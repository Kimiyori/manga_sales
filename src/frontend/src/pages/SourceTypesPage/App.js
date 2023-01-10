import React from "react";
import {   useParams } from 'react-router-dom';
import TypesList from "./TypesList";
import Fetch from "../../components/Fetch";
import styles from "./SourceMainPage.module.css";
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
const SourceTypePage = () => {
    let { source } = useParams();
  return <Fetch uri={`http://127.0.0.1:8080/${source}/`} renderSuccess={MainList} />;
};

export default SourceTypePage;
