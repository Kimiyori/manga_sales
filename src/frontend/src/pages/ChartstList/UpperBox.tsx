import React, { useState, createContext, useEffect } from "react";
import ChartNavigation from "../../components/core/ChartNavigation/ChartNavigation";
import Fetch from "../../hooks/Fetch";
import styles from "./styles.module.scss";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import { TitleCard, TitleData } from "../../components/core/TitleCard/TitleCard";
import { getMonthNumber, getDayNumber } from "../../utils/dates";
import { DatesObject, SourceContextType } from ".";
import { DatesIterator, DatesState } from "../../hooks/DateSwipe";
import { useParams } from "react-router-dom";

export type ContextType = {
  changeMonth: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  changeYear: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  changeDate: (event: React.MouseEvent<HTMLButtonElement>) => void;
  currentDay: string;
};

export const DateContext = createContext<ContextType | null>(null);

const generateUrl = (day: number | string, data: DatesObject[], date: DatesState) => {
  return `${data[date.year_index].year}-${getMonthNumber(
    data[date.year_index].months[date.month_index].name
  )}-${getDayNumber(Number(day) as number)}`;
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

export function ChartLayout({ data }: { data: DatesObject[] }) {
  const { source, type, url_date } = useParams<SourceContextType>();
  const url = `http://127.0.0.1:3000/${source}/${type}/`;
  const [date, changeYear, changeMonth] = DatesIterator(data, url_date);
  const [currentDate, setCurrentDate] = useState<string>(
    url_date ? url_date : generateUrl(data[date.year_index].months[date.month_index].dates.at(-1) as number, data, date)
  );
  const [, currentDay] = currentDate.match(/\d*-\d+-(\d+)/) || [];
  const changeDate = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setCurrentDate(generateUrl(event.currentTarget.textContent as string, data, date));
  };
  useEffect(() => {
    window.history.replaceState(null, "", `${url}${currentDate}`);
  }, [url, currentDate]);
  return (
    <>
        <div className={styles.upper_box}>
          <div className={styles.navigation}>
            <DateContext.Provider value={{ changeYear, changeMonth, changeDate, currentDay }}>
              <ChartNavigation
                year={data[date.year_index]["year"]}
                month={data[date.year_index]["months"][date.month_index].name}
                dates={data[date.year_index]["months"][date.month_index]["dates"]}
              />
            </DateContext.Provider>
          </div>
          <div className={styles.base_menu_info}></div>
        </div>
      </div>
    </>
  );
}
