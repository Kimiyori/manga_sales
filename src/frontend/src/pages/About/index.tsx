import React from "react";
import MainLayout from "../../components/shared/UI/layouts/MainLayout/MainLayout";
import "../../styles/pages/About.scss";

export function AboutInfo() {
  return (
    <>
      <div className={"about"}>
        <div>About this website</div>
        <div>
          <p>
            This site was originally planned as a place where anyone can view sales statistics for manga in Japan from
            Japanese sources in a convenient way and without having to surf through Japanese sites. At the moment, only
            viewing sales charts is available, but in the future it is planned to add detailed statistics for each title
            and category.
          </p>
        </div>
      </div>
    </>
  );
}

export default function About() {
  return <MainLayout section={<AboutInfo />} />;
}
