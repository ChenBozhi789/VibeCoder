import React from 'react';
import type { InputProps } from '../../types';
import { cn } from '../../lib/utils';

export const Input: React.FC<InputProps> = ({
  id,
  label,
  value,
  placeholder,
  onChange,
  hint,
  type = 'text',
  className,
  ...props
}) => {
  return (
    <div className="space-y-1">
      {label && (
        <label 
          htmlFor={id}
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          {label}
        </label>
      )}
      <input
        id={id}
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange?.(e.target.value)}
        className={cn(
          'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
          className
        )}
        {...props}
      />
      {hint && (
        <p className="text-sm text-muted-foreground">{hint}</p>
      )}
    </div>
  );
};
