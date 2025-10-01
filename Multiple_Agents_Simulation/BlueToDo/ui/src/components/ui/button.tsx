import React from 'react';

type Variant = 'primary' | 'ghost';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({ variant = 'primary', children, className = '', ...rest }) => {
  const base = "inline-flex items-center justify-center rounded-md px-3 py-2 text-sm font-medium shadow-sm focus:outline-none focus-visible:ring-2";
  const variants: Record<Variant, string> = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-400",
    ghost: "bg-transparent text-inherit hover:bg-gray-100 focus-visible:ring-gray-300",
  };
  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...rest}>
      {children}
    </button>
  );
};

export default Button;
