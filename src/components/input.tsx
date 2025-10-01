import React from "react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  id: string;
  label?: string;
  hint?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({ id, label, hint, error, className = "", ...rest }) => {
  return (
    <div style={{display:"flex", flexDirection:"column", gap:6}}>
      {label ? <label htmlFor={id} style={{fontWeight:600}}>{label}</label> : null}
      <input id={id} className={["input", className].join(" ")} aria-invalid={!!error} {...rest} />
      {error ? <div role="alert" style={{color:"var(--color-danger)", fontSize:12}}>{error}</div> : hint ? <div style={{color:"var(--color-muted)", fontSize:12}}>{hint}</div> : null}
    </div>
  );
};

export default Input;
