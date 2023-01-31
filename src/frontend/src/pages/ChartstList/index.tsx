import React, { createContext, useEffect } from "react";
import { useParams } from "react-router-dom";
import Fetch from "../../components/Fetch";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import MainLayout from "../../components/shared/UI/layouts/MainLayout/MainLayout";
import { ChartLayout, DatesObject } from "./Layout";
import ListWrapper from "../../components/shared/entity/ItemList/ItemList";
export type SourceContextType = {
  source: string;
  type: string;
};
export const Context = createContext<SourceContextType | null>(null);

export default function ChartList() {
  const { source, type } = useParams<SourceContextType>();
  useEffect(() => {
    document.title = `${source?.toUpperCase()} ${type?.toUpperCase()}  chart`;
  });
  const fetch = (
    <Fetch
      uri={`http://127.0.0.1:8080/${source}/${type}/`}
      renderSuccess={({ data }: { data: DatesObject[] }) => <ChartLayout data={data} />}
      loadingFallback={LoadingComponent}
    />
  );
  return (
    <Context.Provider value={{ source, type } as SourceContextType}>
      <MainLayout section={<ListWrapper component={fetch} />} />;
    </Context.Provider>
  );
}
