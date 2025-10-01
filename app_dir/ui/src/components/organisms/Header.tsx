import React from 'react';
import { Button } from '../atoms/Button';
import { Sun, Moon } from 'lucide-react';

interface HeaderProps {
  onThemeToggle: () => void;
  isDarkMode: boolean;
  onInstall?: () => void;
  canInstall?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  onThemeToggle,
  isDarkMode,
  onInstall,
  canInstall = false
}) => {
  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 py-4 max-w-2xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">HopeTodo</h1>
            <p className="text-sm text-muted-foreground">
              Simple, offline-capable task management
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={onThemeToggle}
              aria-label={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
            >
              {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            
            {canInstall && onInstall && (
              <Button
                variant="outline"
                size="sm"
                onClick={onInstall}
              >
                Install
              </Button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
