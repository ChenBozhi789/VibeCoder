import React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost";
  ariaLabel?: string;
}

export const Button: React.FC<ButtonProps> = ({ variant = "primary", children, className = "", ariaLabel, ...rest }) => {
  const base = "btn";
  const variantClass = variant === "primary" ? "btn-primary" : "btn-ghost";
  return (
    <button
      className={[base, variantClass, className].join(" ")}
      aria-label={ariaLabel}
      {...rest}
    >
      {children}
    </button>
  );
};

export default Button;
