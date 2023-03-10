import React, { createContext, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import styles from "../../styles/pages/ChartList.module.scss";
import { DatesObject, SourceContextType } from ".";
import { DatesIterator } from "../../hooks/DateSwipe";
import { useParams } from "react-router-dom";
import { UpperBox } from "./UpperBox";
import { BottomBox } from "./BottomBox";

export type ContextType = {
  changeMonth: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  changeYear: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  changeDate: (event: React.MouseEvent<HTMLButtonElement>) => void;
  currentDay: string;
  currentDate: string;
  tab: { name: "summary" | "stat" };
  setTab: React.Dispatch<
    React.SetStateAction<{
      name: "summary" | "stat";
    }>
  >;
};
export const DateContext = createContext<ContextType | null>(null);

export function ChartLayout({ data }: { data: DatesObject[] }) {
  const { source, type, url_date } = useParams<SourceContextType>();
  const [searchParams] = useSearchParams();
  const tab_name = searchParams.get("tab") as "summary" | "stat" | null;
  const url = `${source}/${type}`;
  const [date, currentDate, changeYear, changeMonth, changeDate] = DatesIterator(data, url_date);
  const [tab, setTab] = useState<{ name: "summary" | "stat" }>({
    name: tab_name ? tab_name : "summary",
  });
  const [, currentDay] = currentDate.match(/\d*-\d+-(\d+)/) || [];
  useEffect(() => {
    window.history.replaceState(null, "", `/${url}/${currentDate}?tab=${tab.name}`);
  }, [url, currentDate, tab]);
  return (
    <>
      <DateContext.Provider value={{ changeYear, changeMonth, changeDate, currentDay, currentDate, tab, setTab }}>
        <div className={styles.container}>
          <UpperBox data={data} date={date} />
          <BottomBox />
        </div>
      </DateContext.Provider>
    </>
  );
}
