import React from 'react';
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  label?: string;
}
export const Button: React.FC<ButtonProps> = ({ label, children, ...rest }) => {
  return (
    <button {...rest} style={{padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd', background: '#fff'}} aria-label={label}>
      {label ?? children}
    </button>
  );
};
export default Button;
