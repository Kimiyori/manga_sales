import React from "react";
import Navbar from "../../navigations/MainNavigation";
import "./MainLayout.scss";
export default function MainLayout({ section }: { section: JSX.Element }) {
  return (
    <>
      <div className="main-layout">
        <header>
          <Navbar />
        </header>
        <nav></nav>
        <section>{section}</section>
        <aside></aside>
        <footer></footer>
      </div>
    </>
  );
}
