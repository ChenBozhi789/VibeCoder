import React from 'react';
import { Button } from '@/components/ui/button';

export const EmptyState: React.FC<{ onPrimary?: () => void }> = ({ onPrimary }) => {
  return (
    <div className="flex flex-col items-center justify-center p-6 text-center">
      <div className="w-28 h-28 rounded-full bg-blue-50 mb-4 flex items-center justify-center">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" aria-hidden focusable="false">
          <path d="M3 7h18M6 11h12M9 15h6" stroke="#2563eb" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
      <h2 className="text-lg font-semibold mb-2">No tasks yet</h2>
      <p className="text-sm text-muted-foreground mb-4">Quickly add your first task and get productive.</p>
      <Button onClick={onPrimary}>Add first task</Button>
    </div>
  );
};

export default EmptyState;
