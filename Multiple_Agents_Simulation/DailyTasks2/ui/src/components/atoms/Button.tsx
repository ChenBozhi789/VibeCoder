import React from 'react';

export type ButtonProps = {
  children: React.ReactNode;
  variant?: 'primary' | 'ghost';
  disabled?: boolean;
  onClick?: () => void;
  ariaLabel?: string;
};

export const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', disabled = false, onClick, ariaLabel }) => {
  const base = "inline-flex items-center justify-center rounded-md text-sm px-3 py-2 transition";
  const styles =
    variant === 'primary'
      ? base + " bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
      : base + " bg-transparent text-gray-100 hover:bg-gray-800";
  return (
    <button className={styles} onClick={onClick} disabled={disabled} aria-label={ariaLabel}>
      {children}
    </button>
  );
};

export default Button;
