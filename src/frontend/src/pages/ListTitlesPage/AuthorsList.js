import React from "react";
import styles from "./SourceMainPage.module.css";
export default function AuthorsList({ data,name }) {
  return (
    <>
      <p class="author"> {name}: 
      {data.map((item) => ( item ))}
      </p>
    </>
  );
}
