import React, { useState, createContext, useContext, useEffect } from "react";
import ChartNavigation from "../../components/core/ChartNavigation/ChartNavigation";
import Fetch from "../../components/Fetch";
import styles from "./styles.module.scss";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import { TitleCard, TitleData } from "../../components/core/TitleCard/TitleCard";
import { getMonthNumber, getDayNumber } from "../../utils/dates";
import { Context, DatesObject, SourceContextType } from ".";
import { DatesIterator } from "../../hooks/DateSwipe";
export type ContextType = {
  changeMonth: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  changeYear: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  changeDate: (event: React.MouseEvent<HTMLButtonElement>) => void;
  currentDay: string;
};
export const DateContext = createContext<ContextType | null>(null);

export function ChartLayout({ data }: { data: DatesObject[] }) {
  const { source, type, url_date } = useContext(Context) as SourceContextType;
  const url = `http://127.0.0.1:3000/${source}/${type}/`;
  const [date, changeYear, changeMonth] = DatesIterator(data, url_date);
  const generateUrl = (day: number | string) => {
    return `${data[date.year_index].year}-${getMonthNumber(
      data[date.year_index].months[date.month_index].name
    )}-${getDayNumber(Number(day) as number)}`;
  };
  const [currentDate, setCurrentDate] = useState<string>(
    url_date ? url_date : generateUrl(data[date.year_index].months[date.month_index].dates.at(-1) as number)
  );
  const [, currentDay] = currentDate.match(/\d*-\d+-(\d+)/) || [];
  const changeDate = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setCurrentDate(generateUrl(event.currentTarget.textContent as string));
  };
  useEffect(() => {
    window.history.replaceState(null, "", `${url}${currentDate}`);
  }, [url, currentDate]);
  return (
    <>
      <div>
        <DateContext.Provider value={{ changeYear, changeMonth, changeDate, currentDay }}>
          <ChartNavigation
            year={data[date.year_index]["year"]}
            month={data[date.year_index]["months"][date.month_index].name}
            dates={data[date.year_index]["months"][date.month_index]["dates"]}
          />
        </DateContext.Provider>
      </div>
      <div className={styles["list_items"]}>
        {currentDate ? (
          <Fetch
            uri={`http://127.0.0.1:8080/${source}/${type}/${currentDate}/`}
            renderSuccess={({ data }: { data: TitleData[] }) =>
              data.map((title, i) => <TitleCard key={i} title_data={title} date={currentDate} />)
            }
            loadingFallback={LoadingComponent}
          />
        ) : (
          <div>1</div>
        )}
      </div>
    </>
  );
}
