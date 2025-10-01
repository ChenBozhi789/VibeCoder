import React from 'react';
import type { CardProps } from '../../types';
import { cn } from '../../lib/utils';

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  children,
  className
}) => {
  return (
    <div className={cn(
      'rounded-lg border bg-card text-card-foreground shadow-sm',
      className
    )}>
      <div className="p-6">
        {title && (
          <h3 className="text-lg font-semibold leading-none tracking-tight">
            {title}
          </h3>
        )}
        {subtitle && (
          <p className="text-sm text-muted-foreground mt-1">
            {subtitle}
          </p>
        )}
        <div className="mt-4">
          {children}
        </div>
      </div>
    </div>
  );
};
