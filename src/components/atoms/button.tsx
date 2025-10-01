
import React from "react";

export interface ButtonProps {
  label?: string;
  onClick?: (e?: React.MouseEvent) => void;
  variant?: "primary" | "secondary" | "ghost";
  disabled?: boolean;
  ariaLabel?: string;
  type?: "button" | "submit" | "reset";
  className?: string;
}

const classFor = (variant?: string) => {
  switch (variant) {
    case "ghost": return "btn btn-ghost";
    case "secondary": return "btn";
    default: return "btn btn-primary";
  }
};

const Button: React.FC<ButtonProps> = ({ label, onClick, variant="primary", disabled=false, ariaLabel, type="button", className }) => {
  return (
    <button
      type={type}
      className={classFor(variant) + (className ? ` ${className}` : "")}
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel || label}
    >
      {label}
    </button>
  );
};

export default Button;
