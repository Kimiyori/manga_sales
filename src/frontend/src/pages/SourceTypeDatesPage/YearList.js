import React from "react";
import MonthsList from "./MonthList";
import PropTypes from "prop-types";
export default function YearsList({ data = {} }) {
  return (
    <>
      {data.map((year) =>
        Object.keys(year).map((k) => (
          <MonthsList key={k} year={k} months_list={year[k]} />
        ))
      )}
    </>
  );
}
YearsList.propTypes = {
  data: PropTypes.shape(),
};
