import React, { useState, useEffect, useContext } from "react";
import ChartNavigation from "../../components/core/ChartNavigation/ChartNavigation";
import { calculate, compare } from "../../utils/calculate";
import { Context, SourceContextType } from ".";
import Fetch from "../../components/Fetch";
import styles from "./styles.module.scss";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import { TitleCard, TitleData } from "../../components/core/TitleCard/TitleCard";
export interface DatesObject {
  year: string;
  months: { name: string; dates: number[] }[];
}
const getMonthNumber = (monthName: string) => {
  return String(new Date(`${monthName} 1, 2022`).getMonth() + 1).padStart(2, "0");
};
const getDayNumber = (dayNumber: number) => {
  return String(dayNumber).padStart(2, "0");
};
const DatesIterator = (
  data: DatesObject[]
): [
  { year: number; month: number },
  (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void,
  (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void
] => {
  const [date, setDate] = useState({
    year: data.length - 1,
    month: data[data.length - 1]["months"].length - 1,
  });
  const changeMonth = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    const direction = event.currentTarget.dataset.arrow == "left";
    const operator = direction ? "-" : "+";
    const comparison = direction ? "<" : ">";
    const new_month = calculate(date.month, 1, operator);
    if (compare(new_month, direction ? 0 : data[date.year]["months"].length - 1, comparison)) {
      const guessed_year = calculate(date.year, 1, operator);
      if (!compare(guessed_year, direction ? 0 : data.length - 1, comparison)) {
        setDate({
          month: direction ? data[guessed_year]["months"].length - 1 : 0,
          year: Math.min(guessed_year, data.length - 1),
        });
        return;
      }
    }
    setDate({ ...date, month: Math.max(0, Math.min(new_month, data[date.year]["months"].length - 1)) });
  };
  const changeYear = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    const direction = event.currentTarget.dataset.arrow == "left";
    const operator = direction ? "-" : "+";
    const comparison = direction ? "<" : ">";
    const new_year = calculate(date.year, 1, operator);
    if (!compare(new_year, direction ? 0 : data.length - 1, comparison)) {
      setDate({
        month: direction ? data[new_year]["months"].length - 1 : 0,
        year: new_year,
      });
    }
  };
  return [date, changeYear, changeMonth];
};
export function ChartLayout({ data }: { data: DatesObject[] }) {
  const { source, type } = useContext(Context) as SourceContextType;
  const [date, changeYear, changeMonth] = DatesIterator(data);
  const [currentDate, setCurrentDate] = useState<string>();
  useEffect(() => {
    setCurrentDate(
      `http://127.0.0.1:8080/${source}/${type}/${data[date.year].year}-${getMonthNumber(
        data[date.year].months[date.month].name
      )}-${getDayNumber(data[date.year].months[date.month].dates.at(-1) as number)}/`
    );
  }, []);
  const changeDate = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setCurrentDate(
      `http://127.0.0.1:8080/${source}/${type}/${data[date.year].year}-${getMonthNumber(
        data[date.year].months[date.month].name
      )}-${getDayNumber(Number(event.currentTarget.textContent) as number)}/`
    );
  };
  return (
    <>
      <div>
        <ChartNavigation
          year={data[date.year]["year"]}
          month={data[date.year]["months"][date.month].name}
          dates={data[date.year]["months"][date.month]["dates"]}
          changeMonth={changeMonth}
          changeYear={changeYear}
          changeData={changeDate}
        />
      </div>
      <div className={styles["list_items"]}>
        {currentDate ? (
          <Fetch
            uri={currentDate}
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
