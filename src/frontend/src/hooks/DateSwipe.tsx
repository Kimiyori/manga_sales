import React, { useState } from "react";
import { DatesObject } from "../pages/ChartstList";
import { calculate, compare } from "../utils/calculate";
import { getDayNumber, getMonthName, getMonthNumber } from "../utils/dates";

export type DatesState = { year_index: number; month_index: number };
const getYear = (data: DatesObject[], date: string) => {
  const [, url_year] = date.match(/(\d+)-\d+-\d+/) || [];
  const finded_year = data.map((obj) => obj.year).indexOf(url_year);
  return finded_year;
};
const getMonth = (data: DatesObject[], date: string, year: number) => {
  const [, month] = date.match(/\d+-(\d+)-\d+/) || [];
  const finded_month = data[year]["months"].map((obj) => obj.name).indexOf(getMonthName(Number(month)));
  return finded_month;
};
const generateDateString = (day: number | string, data: DatesObject[], date: DatesState) => {
  return `${data[date.year_index].year}-${getMonthNumber(
    data[date.year_index].months[date.month_index].name
  )}-${getDayNumber(Number(day) as number)}`;
};
export const DatesIterator = (
  data: DatesObject[],
  url_date?: string
): [
  DatesState,
  string,
  (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void,
  (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void,
  (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void
] => {
  const year = url_date ? getYear(data, url_date) ?? data.length - 1 : data.length - 1;
  const month = url_date ? getMonth(data, url_date, year) : data[data.length - 1]["months"].length - 1;
  const [date, setDate] = useState({
    year_index: year,
    month_index: month,
  });
  const [currentDate, setCurrentDate] = useState<string>(
    url_date
      ? url_date
      : generateDateString(data[date.year_index].months[date.month_index].dates.at(-1) as number, data, date)
  );
  const changeDate = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setCurrentDate(generateDateString(event.currentTarget.textContent as string, data, date));
  };
  const changeMonth = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    const direction = event.currentTarget.dataset.arrow == "left";
    const operator = direction ? "-" : "+";
    const comparison = direction ? "<" : ">";
    const new_month = calculate(date.month_index, 1, operator);
    if (compare(new_month, direction ? 0 : data[date.year_index]["months"].length - 1, comparison)) {
      const guessed_year = calculate(date.year_index, 1, operator);
      if (!compare(guessed_year, direction ? 0 : data.length - 1, comparison)) {
        setDate({
          month_index: direction ? data[guessed_year]["months"].length - 1 : 0,
          year_index: Math.min(guessed_year, data.length - 1),
        });
        return;
      }
    }
    setDate({ ...date, month_index: Math.max(0, Math.min(new_month, data[date.year_index]["months"].length - 1)) });
  };
  const changeYear = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    const direction = event.currentTarget.dataset.arrow == "left";
    const operator = direction ? "-" : "+";
    const comparison = direction ? "<" : ">";
    const new_year = calculate(date.year_index, 1, operator);
    if (!compare(new_year, direction ? 0 : data.length - 1, comparison)) {
      setDate({
        month_index: direction ? data[new_year]["months"].length - 1 : 0,
        year_index: new_year,
      });
    }
  };
  return [date, currentDate, changeYear, changeMonth, changeDate];
};
