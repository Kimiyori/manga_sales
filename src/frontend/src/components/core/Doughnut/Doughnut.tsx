import React from "react";
import { Chart as ChartJS, ArcElement, Tooltip, Legend, Colors } from "chart.js";
import { Doughnut } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend, Colors);

export function DoughnutChart({ label, labels, chartData }: { label: string; labels: string[]; chartData: number[] }) {
  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "bottom" as const,
      },
      colors: {
        enabled: true,
      },
    },
  };
  const dataPie = {
    labels: labels,
    datasets: [
      {
        label: label,
        data: chartData,
      },
    ],
  };
  return <Doughnut options={options} data={dataPie} />;
}
