import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  value?: string;
  onChange?: (v: string) => void;
  ariaLabel?: string;
}

export const Input: React.FC<InputProps> = ({ value, onChange, ariaLabel, className = '', ...rest }) => {
  return (
    <input
      className={`px-3 py-2 border rounded-md focus:ring-2 focus:outline-none ${className}`}
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
      aria-label={ariaLabel}
      {...rest}
    />
  );
};

export default Input;
