import React from "react";

export default function NavElement({ title, path }: { title: string; path: string }) {
  return (
    <>
      <li>
        <a href={path}>{title}</a>
      </li>
    </>
  );
}
