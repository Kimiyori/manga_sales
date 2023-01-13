import React, { createContext } from "react";
import { useParams } from "react-router-dom";
import Fetch from "../../components/Fetch";
import LoadingComponent from "../../components/LoadingComponent/loadingComponent";
import TitlesList from "./TitlesList";
import ListWrapper from "../../components/List/ListWrapper";
export const Context = createContext();

export default function TitlesListMain() {
  let { source, type, date } = useParams();
  let fetch = (
    <Fetch
      uri={`http://127.0.0.1:8080/${source}/${type}/${date}/`}
      renderSuccess={TitlesList}
      loadingFallback={LoadingComponent}
    />
  );
  return (
    <>
      <Context.Provider value={{ source, type, date }}>
        <ListWrapper title="Rating" component={fetch} />
      </Context.Provider>
    </>
  );
}
