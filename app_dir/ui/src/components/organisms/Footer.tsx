import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t bg-card mt-auto">
      <div className="container mx-auto px-4 py-4 max-w-2xl">
        <div className="text-center text-sm text-muted-foreground">
          <p>HopeTodo - Simple, offline-capable task management</p>
        </div>
      </div>
    </footer>
  );
};
