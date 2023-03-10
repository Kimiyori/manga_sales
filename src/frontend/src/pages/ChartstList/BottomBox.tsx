import React, { useContext } from "react";
import Fetch from "../../hooks/Fetch";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import { TitleCard, TitleData } from "../../components/core/TitleCard/TitleCard";
import { SourceContextType } from ".";
import { useParams } from "react-router-dom";
import { ContextType, DateContext } from "./Layout";
import StatCharts from "./StatComponent";
import styles from "../../styles/pages/ChartList.module.scss";

const ListTitles = ({ data, currentDate }: { data: TitleData[]; currentDate: string }) => {
  return (
    <>
      {data.map((title, i) => (
        <TitleCard key={i} title_data={title} date={currentDate} />
      ))}
    </>
  );
};

export function BottomBox() {
  const { source, type } = useParams<SourceContextType>();
  const { currentDate, tab } = useContext(DateContext) as ContextType;
  return (
    <>
      {currentDate && (
        <Fetch<TitleData[]>
          uri={`${process.env.REACT_APP_BACKEND_URL}/source/${source}/${type}/${currentDate}`}
          renderSuccess={({ data }) => {
            switch (tab.name) {
              case "summary":
                return (
                  <div className={styles.bottom_box}>
                    <ListTitles data={data} currentDate={currentDate} />
                  </div>
                );
              case "stat":
                return <StatCharts data={data} />;
            }
          }}
          loadingFallback={LoadingComponent}
        />
      )}
    </>
  );
}
