import React from 'react';
import { cn } from '../../lib/utils';

interface CharacterCounterProps {
  current: number;
  max: number;
  showWarning?: boolean;
}

export const CharacterCounter: React.FC<CharacterCounterProps> = ({
  current,
  max,
  showWarning = false
}) => {
  const remaining = max - current;
  const isOverLimit = current > max;

  return (
    <div className="flex justify-end">
      <span
        className={cn(
          'text-xs text-muted-foreground',
          showWarning && 'text-yellow-600 dark:text-yellow-400',
          isOverLimit && 'text-red-600 dark:text-red-400'
        )}
      >
        {remaining} characters remaining
      </span>
    </div>
  );
};
