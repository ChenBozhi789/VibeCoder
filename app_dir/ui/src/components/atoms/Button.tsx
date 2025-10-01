import React from 'react';
import type { ButtonProps } from '../../types';
import { cn } from '../../lib/utils';

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'default',
  onClick,
  disabled = false,
  ariaLabel,
  className,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2';
  
  const variantClasses = {
    primary: 'bg-primary text-primary-foreground shadow hover:bg-primary/90',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
    outline: 'border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground'
  };

  const sizeClasses = {
    sm: 'h-8 px-3 text-xs',
    default: 'h-9 px-4 py-2',
    lg: 'h-10 px-6 text-base'
  };

  return (
    <button
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      {...props}
    >
      {children}
    </button>
  );
};
