import React, { useLayoutEffect } from "react";
import { useParams } from "react-router-dom";
import MainLayout from "../../components/shared/UI/layouts/MainLayout/MainLayout";
import { ChartLayout } from "./Layout";
import { capitalize } from "../../utils/string_helpers";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import Fetch from "../../hooks/Fetch";
export type SourceContextType = {
  source: string;
  type: string;
  url_date?: string;
};
export interface DatesObject {
  year: string;
  months: { name: string; dates: number[] }[];
}

export default function ChartList() {
  const { source, type } = useParams<SourceContextType>();
  useLayoutEffect(() => {
    document.title = `${capitalize(source as string)} ${capitalize(type as string)}  chart`;
  });
  return (
    <MainLayout
      section={
        <Fetch<DatesObject[]>
          uri={`http://127.0.0.1:8080/${source}/${type}/`}
          renderSuccess={({ data }) => <ChartLayout data={data} />}
          loadingFallback={LoadingComponent}
        />
      }
    />
  );
}
