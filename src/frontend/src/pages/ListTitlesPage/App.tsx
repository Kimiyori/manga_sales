import React, { createContext } from "react";
import { useParams } from "react-router-dom";
import Fetch from "../../components/Fetch";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import TitlesList from "./TitlesList";
import ListWrapper from "../../components/shared/entity/ItemList/ItemList";
export const Context = createContext<any>({});

export default function TitlesListMain() {
  const { source, type, date } = useParams();
  const fetch = (
    <Fetch
      uri={`http://127.0.0.1:8080/${source}/${type}/${date}/`}
      renderSuccess={TitlesList}
      loadingFallback={LoadingComponent}
    />
  );
  return (
    <>
      <Context.Provider value={{ source, type, date }}>
        <ListWrapper component={fetch} />
      </Context.Provider>
    </>
  );
}
