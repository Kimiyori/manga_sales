import { faker } from "@faker-js/faker";
import { DatesObject } from "../ChartNavigation";
function subtractYears(date: Date, years: number) {
  date.setFullYear(date.getFullYear() - years);
  return date;
}
export function createRandomYear(from: Date, to: Date): DatesObject {
  return {
    year: faker.date.between(from, to).getFullYear().toString(),
    months: [{ name: faker.date.month(), dates: Array.from({ length: 5 }, () => faker.datatype.number()) }],
  };
}
export function createRandomYearList(length: number): DatesObject[] {
  return Array.from({ length: length }, (_, index) =>
    createRandomYear(subtractYears(new Date(Date.now()), index + 1), subtractYears(new Date(Date.now()), index))
  );
}
