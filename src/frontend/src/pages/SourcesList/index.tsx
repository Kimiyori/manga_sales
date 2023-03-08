import React from "react";
import MainLayout from "../../components/shared/UI/layouts/MainLayout/MainLayout";
import Fetch from "../../hooks/Fetch";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import ListWrapper from "../../components/shared/entity/ItemList/ItemList";
import Item, { ItemData } from "../../components/core/ItemBlock/ItemBlock";
import "../../styles/pages/SourcesList.scss";
import ChangePageTitle from "../../hooks/ChangePageTitle";
function SourceList({ data = [] }: { data: ItemData[] }) {
  return (
    <>
      {data.map((source, i) => (
        <Item key={i} data={source} />
      ))}
    </>
  );
}
export default function SourceListMainPage() {
  const fetch = (
    <Fetch
      uri={`${process.env.REACT_APP_BACKEND_URL}/source`}
      renderSuccess={SourceList}
      loadingFallback={LoadingComponent}
    />
  );
  return (
    <>
      <ChangePageTitle pageTitle="Sources" />
      <MainLayout
        section={
          <div className="container">
            <ListWrapper component={fetch} />
          </div>
        }
      />
    </>
  );
}
