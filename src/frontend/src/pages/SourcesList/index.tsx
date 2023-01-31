import React, { useEffect } from "react";
import MainLayout from "../../components/shared/UI/layouts/MainLayout/MainLayout";
import Fetch from "../../components/Fetch";
import LoadingComponent from "../../components/core/LoadingComponent/loadingComponent";
import ListWrapper from "../../components/shared/entity/ItemList/ItemList";
import Item, { ItemData } from "../../components/core/ItemBlock/ItemBlock";

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
  useEffect(() => {
    document.title = "Manga Statistics sources";
  }, []);
  const fetch = (
    <>
      <Fetch uri={`http://127.0.0.1:8080`} renderSuccess={SourceList} loadingFallback={LoadingComponent} />
    </>
  );
  return <MainLayout section={<ListWrapper component={fetch} />} />;
}
