import React, { createContext, useLayoutEffect } from "react";
import { useParams } from "react-router-dom";
import Fetch from "../../components/Fetch";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import MainLayout from "../../components/shared/UI/layouts/MainLayout/MainLayout";
import { ChartLayout } from "./Layout";
import ListWrapper from "../../components/shared/entity/ItemList/ItemList";
import { capitalize } from "../../utils/string_helpers";
export type SourceContextType = {
  source: string;
  type: string;
  url_date?: string;
};
export interface DatesObject {
  year: string;
  months: { name: string; dates: number[] }[];
}
export const Context = createContext<SourceContextType | null>(null);

export default function ChartList() {
  const { source, type, url_date } = useParams<SourceContextType>();
  useLayoutEffect(() => {
    document.title = `${capitalize(source as string)} ${capitalize(type as string)}  chart`;
  });
  const fetch = (
    <Fetch
      uri={`http://127.0.0.1:8080/${source}/${type}/`}
      renderSuccess={({ data }: { data: DatesObject[] }) => <ChartLayout data={data} />}
      loadingFallback={LoadingComponent}
    />
  );
  return (
    <Context.Provider value={{ source, type, url_date } as SourceContextType}>
      <MainLayout section={<ListWrapper component={fetch} />} />
    </Context.Provider>
  );
}
