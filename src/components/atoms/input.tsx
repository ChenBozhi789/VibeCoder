
import React from "react";

export interface TextInputProps {
  id?: string;
  value?: string;
  placeholder?: string;
  onChange?: (value: string) => void;
  ariaLabel?: string;
  name?: string;
  disabled?: boolean;
  type?: string;
}

const TextInput: React.FC<TextInputProps> = ({ id, value="", placeholder, onChange, ariaLabel, name, disabled=false, type="text" }) => {
  return (
    <input
      id={id}
      name={name}
      className="input"
      value={value}
      onChange={(e) => onChange && onChange(e.target.value)}
      placeholder={placeholder}
      aria-label={ariaLabel || placeholder}
      disabled={disabled}
      type={type}
    />
  );
};

export default TextInput;
