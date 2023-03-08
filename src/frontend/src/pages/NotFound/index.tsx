import React from "react";
import MainLayout from "../../components/shared/UI/layouts/MainLayout/MainLayout";
import ChangePageTitle from "../../hooks/ChangePageTitle";
import "../../styles/pages/NotFound.scss";

export function NotFoundElement() {
  return (
    <>
      <div className={"not-found"}>
        <div>404</div>
        <div>Error</div>
      </div>
    </>
  );
}

export default function NotFound() {
  return (
    <>
      <ChangePageTitle pageTitle="Not found page" />
      <MainLayout section={<NotFoundElement />} />
    </>
  );
}
