import React from "react";
import { DoughnutChart } from "../../components/core/Doughnut/Doughnut";
import { PieChart } from "../../components/core/Pie/Pie";
import { TitleData } from "../../components/core/TitleCard/TitleCard";
import { VerticalBar } from "../../components/core/VerticalBar/VerticalBar";
import "../../styles/components/_chart_stat.scss";
const SalesBar = ({ data }: { data: TitleData[] }) => {
  return <VerticalBar label="Titles" labels={data.map((row) => row.title)} chartData={data.map((row) => row.sales)} />;
};

const SalesByPublisher = ({ data }: { data: TitleData[] }) => {
  const pieData: { [key: string]: number } = {};
  data.forEach((row) => {
    row.publishers.forEach((element) => {
      if (element in pieData) {
        pieData[element] += row.sales as number;
      } else {
        pieData[element] = row.sales as number;
      }
    });
  });
  return (
    <PieChart label="Sales" labels={Object.keys(pieData).slice(0, 5)} chartData={Object.values(pieData).slice(0, 5)} />
  );
};

const SalesByAuthor = ({ data }: { data: TitleData[] }) => {
  const pieData: { [key: string]: number } = {};
  data.forEach((row) => {
    row.authors.forEach((element) => {
      if (element in pieData) {
        pieData[element] += row.sales as number;
      } else {
        pieData[element] = row.sales as number;
      }
    });
  });
  return (
    <PieChart label="Sales" labels={Object.keys(pieData).slice(0, 5)} chartData={Object.values(pieData).slice(0, 5)} />
  );
};

const MostCommonAuthors = ({ data }: { data: TitleData[] }) => {
  const pieData: { [key: string]: number } = {};
  data.forEach((row) => {
    row.authors.forEach((element) => {
      if (element in pieData) {
        pieData[element] += 1;
      } else {
        pieData[element] = 1;
      }
    });
  });
  return (
    <DoughnutChart
      label="Number of titles"
      labels={Object.keys(pieData).slice(0, 5)}
      chartData={Object.values(pieData).slice(0, 5)}
    />
  );
};
const MostCommonPublishers = ({ data }: { data: TitleData[] }) => {
  const pieData: { [key: string]: number } = {};
  data.forEach((row) => {
    row.publishers.forEach((element) => {
      if (element in pieData) {
        pieData[element] += 1;
      } else {
        pieData[element] = 1;
      }
    });
  });
  return (
    <DoughnutChart
      label="Number of titles"
      labels={Object.keys(pieData).slice(0, 5)}
      chartData={Object.values(pieData).slice(0, 5)}
    />
  );
};
const StatCharts = ({ data }: { data: TitleData[] }) => {
  return (
    <>
      <div className="stat_container">
        {data[0].sales && (
          <div className="sales_charts">
            <div className="sales_bar">
              <p>Sales Bar</p>
              <SalesBar data={data} />
            </div>
            <div className="publishers_pie">
              <p>Top 5 publishers by sales</p>
              <SalesByPublisher data={data} />
            </div>
            <div className="authors_pie">
              <p>Top 5 authors by sales</p>
              <SalesByAuthor data={data} />
            </div>
          </div>
        )}
        <div className="no_sales_charts">
          <div className="authors_doughnut">
            <p>Top authors by appearance</p>
            <MostCommonAuthors data={data} />
          </div>
          <div className="publishers_doughnut">
            <p>Top publishers by appearance</p>
            <MostCommonPublishers data={data} />
          </div>
        </div>
      </div>
    </>
  );
};
export default StatCharts;
