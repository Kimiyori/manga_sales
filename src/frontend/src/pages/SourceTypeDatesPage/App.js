import React, { createContext } from "react";
import { useParams } from "react-router-dom";
import YearsList from "./YearList";
import Fetch from "../../components/Fetch";
import LoadingComponent from "../../components/LoadingComponent/loadingComponent";
import ListWrapper from "../../components/List/ListWrapper";
export const Context = createContext();

export default function SourceTypeDatesPage() {
  let { source } = useParams();
  let { type } = useParams();
  let fetch = (
    <Fetch
      uri={`http://127.0.0.1:8080/${source}/${type}/`}
      renderSuccess={YearsList}
      loadingFallback={LoadingComponent}
    />
  );
  return (
    <Context.Provider value={{ source, type }}>
      <ListWrapper title="Dates" component={fetch} />
    </Context.Provider>
  );
}
