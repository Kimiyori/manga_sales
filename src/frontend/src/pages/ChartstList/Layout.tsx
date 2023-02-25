import React, { createContext, useEffect } from "react";
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
};

export const DateContext = createContext<ContextType | null>(null);

export function ChartLayout({ data }: { data: DatesObject[] }) {
  const { source, type, url_date } = useParams<SourceContextType>();
  const url = `${source}/${type}`;
  const [date, currentDate, changeYear, changeMonth, changeDate] = DatesIterator(data, url_date);
  const [, currentDay] = currentDate.match(/\d*-\d+-(\d+)/) || [];
  useEffect(() => {
    window.history.replaceState(null, "", `/${url}/${currentDate}`);
  }, [url, currentDate]);
  return (
    <>
      <div className={styles.container}>
        <DateContext.Provider value={{ changeYear, changeMonth, changeDate, currentDay }}>
          <div className={styles.upper_box}>
            <UpperBox data={data} date={date} />
          </div>
        </DateContext.Provider>
        <div className={styles.bottom_box}>
          <BottomBox currentDate={currentDate} />
        </div>
      </div>
    </>
  );
}
