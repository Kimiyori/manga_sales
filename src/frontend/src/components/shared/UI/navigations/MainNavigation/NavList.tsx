import React from "react";
import NavElement from "./NavElement";

export default function NavList({ items }: { items: { path: string; name: string }[] }) {
  return (
    <>
      <ul>
        {items.map((item, i) => (
          <NavElement key={i} title={item.name} path={item.path} />
        ))}
      </ul>
    </>
  );
}
