import React, { createContext } from "react";
import { useParams } from "react-router-dom";
import YearsList from "./YearList";
import Fetch from "../../components/Fetch";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import ListWrapper from "../../components/shared/entity/ItemList/ItemList";
export const Context = createContext<any>({});

export default function SourceTypeDatesPage() {
  const { source } = useParams();
  const { type } = useParams();
  const fetch = (
    <Fetch
      uri={`http://127.0.0.1:8080/${source}/${type}/`}
      renderSuccess={YearsList}
      loadingFallback={LoadingComponent}
    />
  );
  return (
    <Context.Provider value={{ source, type }}>
      <ListWrapper component={fetch} />
    </Context.Provider>
  );
}
