import React from "react";

export interface CardProps {
  title?: string;
  subtitle?: string;
  children?: React.ReactNode;
  className?: string;
}

const Card: React.FC<CardProps> = ({ title, subtitle, children, className = "" }) => {
  return (
    <section className={["card", className].join(" ")} aria-labelledby={title ? "card-title" : undefined}>
      {title ? <div id="card-title" className="card-title">{title}</div> : null}
      {subtitle ? <div className="card-sub">{subtitle}</div> : null}
      <div>{children}</div>
    </section>
  );
};

export default Card;
