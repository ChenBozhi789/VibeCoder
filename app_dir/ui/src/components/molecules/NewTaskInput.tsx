import React, { useState } from 'react';
import { Input } from '../atoms/Input';
import { CharacterCounter } from '../atoms/CharacterCounter';
import { Button } from '../atoms/Button';
import { Plus } from 'lucide-react';

interface NewTaskInputProps {
  onSubmit: (title: string) => void;
  disabled?: boolean;
}

export const NewTaskInput: React.FC<NewTaskInputProps> = ({
  onSubmit,
  disabled = false
}) => {
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const trimmedTitle = title.trim();
    
    if (!trimmedTitle) {
      setError('Title is required');
      return;
    }
    
    if (trimmedTitle.length > 50) {
      setError('Title must be 50 characters or less');
      return;
    }
    
    setError('');
    onSubmit(trimmedTitle);
    setTitle('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  const handleChange = (value: string) => {
    setTitle(value);
    if (error) {
      setError('');
    }
  };

  const isInvalid = title.length > 50 || (title.trim().length === 0 && title.length > 0);

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <div className="flex gap-2">
        <div className="flex-1">
          <Input
            value={title}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="Add a task…"
            maxLength={50}
            error={error}
            disabled={disabled}
            autoFocus
          />
          <CharacterCounter
            current={title.length}
            max={50}
            showWarning={title.length > 40}
          />
        </div>
        <Button
          type="submit"
          disabled={disabled || !title.trim() || title.length > 50}
          size="sm"
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>
    </form>
  );
};
