import React from "react";
import { useParams } from "react-router-dom";
import MainLayout from "../../components/shared/UI/layouts/MainLayout/MainLayout";
import { ChartLayout } from "./Layout";
import { capitalize } from "../../utils/string_helpers";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import Fetch from "../../hooks/Fetch";
import ChangePageTitle from "../../hooks/ChangePageTitle";
export type SourceContextType = {
  source: string;
  type: string;
  url_date?: string;
  stat?: string;
};
export interface DatesObject {
  year: string;
  months: { name: string; dates: number[] }[];
}

export default function ChartList() {
  const { source, type } = useParams<SourceContextType>();
  return (
    <>
      <ChangePageTitle pageTitle={`${capitalize(source as string)} ${capitalize(type as string)}  chart`} />
      <MainLayout
        section={
          <Fetch<DatesObject[]>
            uri={`${process.env.REACT_APP_BACKEND_URL}/source/${source}/${type}`}
            renderSuccess={({ data }) => <ChartLayout data={data} />}
            loadingFallback={LoadingComponent}
          />
        }
      />
    </>
  );
}
