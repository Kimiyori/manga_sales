import React, { createContext } from "react";
import { useParams } from "react-router-dom";
import TypesList from "./TypesList";
import Fetch from "../../components/Fetch";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import ListWrapper from "../../components/shared/entity/ItemList/ItemList";

export const Context = createContext<any>({});

export default function SourceTypePage() {
  const { source } = useParams();
  const fetch = (
    <Fetch uri={`http://127.0.0.1:8080/${source}/`} renderSuccess={TypesList} loadingFallback={LoadingComponent} />
  );
  return (
    <Context.Provider value={{ source }}>
      <ListWrapper component={fetch} />
    </Context.Provider>
  );
}
