import React from 'react';

export type TextInputProps = {
  value: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  ariaLabel?: string;
  className?: string;
};

export const TextInput: React.FC<TextInputProps> = ({ value, onChange, placeholder = '', ariaLabel, className = '' }) => {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
      placeholder={placeholder}
      aria-label={ariaLabel}
      className={
        "w-full rounded-md bg-gray-900 text-white px-3 py-2 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 " +
        className
      }
    />
  );
};

export default TextInput;
