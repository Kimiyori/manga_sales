import React from "react";
import Fetch from "../../hooks/Fetch";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import { TitleCard, TitleData } from "../../components/core/TitleCard/TitleCard";
import { SourceContextType } from ".";
import { useParams } from "react-router-dom";

export type ContextType = {
  changeMonth: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  changeYear: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  changeDate: (event: React.MouseEvent<HTMLButtonElement>) => void;
  currentDay: string;
};

const ListTitles = ({ data, currentDate }: { data: TitleData[]; currentDate: string }) => {
  return (
    <>
      {data.map((title, i) => (
        <TitleCard key={i} title_data={title} date={currentDate} />
      ))}
    </>
  );
};

export function BottomBox({ currentDate }: { currentDate: string }) {
  const { source, type } = useParams<SourceContextType>();
  return (
    <>
      {currentDate && (
        <Fetch<TitleData[]>
          uri={`/api/source/${source}/${type}/${currentDate}`}
          renderSuccess={({ data }) => <ListTitles data={data} currentDate={currentDate} />}
          loadingFallback={LoadingComponent}
        />
      )}
    </>
  );
}
