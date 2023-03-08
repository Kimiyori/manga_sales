import React from "react";
import MainLayout from "../../components/shared/UI/layouts/MainLayout/MainLayout";
import { BsTelegram } from "react-icons/bs";
import "../../styles/pages/Contact.scss";
import ChangePageTitle from "../../hooks/ChangePageTitle";

export function ContactInfo() {
  return (
    <>
      <div className={"contact"}>
        <div>Contact info:</div>
        <div className={"links"}>
          <a href="https://t.me/tooooooook">
            <BsTelegram /> <span>@tooooooook</span>
          </a>
        </div>
      </div>
    </>
  );
}

export default function Contact() {
  return (
    <>
      <ChangePageTitle pageTitle="Contact info" />
      <MainLayout section={<ContactInfo />} />
    </>
  );
}
