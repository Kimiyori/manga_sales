// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import React from "react";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend, Colors } from "chart.js";
import gradient from "chartjs-plugin-gradient";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend, Colors, gradient);
export function VerticalBar<T>({ label, labels, chartData }: { label: string; labels: string[]; chartData: T }) {
  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
      gradient,
    },
    scales: {
      x: {
        display: false,
      },
    },
  };
  const barData = {
    labels,
    datasets: [
      {
        label: label,
        data: chartData,
        gradient: {
          backgroundColor: {
            axis: "x",
            colors: {
              0: "#FDB6FE",
              50: "8CE5FF",
              100: "#8CFFAB",
            },
          },
        },
      },
    ],
  };
  return <Bar options={options} data={barData} />;
}
