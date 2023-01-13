import React from "react";
import SourceList from "./SourceList";
import Fetch from "../../components/Fetch";
import LoadingComponent from "../../components/LoadingComponent/loadingComponent";
import ListWrapper from "../../components/List/ListWrapper";


export default function SourceListMainPage() {
  let fetch=<Fetch
  uri={`http://127.0.0.1:8080`}
  renderSuccess={SourceList}
  loadingFallback={LoadingComponent}
/>
  return (
    <ListWrapper title='Sources' component={fetch} />
  );
}
