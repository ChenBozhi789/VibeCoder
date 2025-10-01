import React from 'react';
import { Check } from 'lucide-react';
import { cn } from '../../lib/utils';

interface CheckboxProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

export const Checkbox: React.FC<CheckboxProps> = ({
  checked,
  onChange,
  disabled = false
}) => {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      disabled={disabled}
      className={cn(
        'h-5 w-5 rounded border-2 flex items-center justify-center transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary',
        checked
          ? 'bg-primary border-primary text-primary-foreground'
          : 'border-input hover:border-primary',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
      aria-checked={checked}
      role="checkbox"
    >
      {checked && <Check className="h-3 w-3" />}
    </button>
  );
};
