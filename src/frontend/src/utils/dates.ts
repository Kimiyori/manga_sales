export const getMonthNumber = (monthName: string) => {
  return String(new Date(`${monthName} 1, 2022`).getMonth() + 1).padStart(2, "0");
};
export const getMonthName = (monthNumber: number) => {
  const date = new Date();
  date.setMonth(monthNumber - 1);

  return date.toLocaleString("en-US", { month: "long" });
};
export const getDayNumber = (dayNumber: number) => {
  return String(dayNumber).padStart(2, "0");
};
