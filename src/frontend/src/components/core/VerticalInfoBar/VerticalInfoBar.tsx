import React from "react";

export default function VerticalInfoBar({ title, data }: { title: string; data: string | number | React.ReactNode }) {
  return (
    <>
      <div>{title}</div>
      <div>{data ? data : "None"}</div>
    </>
  );
}
