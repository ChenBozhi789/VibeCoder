import React, { useState, useRef, useEffect } from 'react';
import { Checkbox } from '../atoms/Checkbox';
import { Button } from '../atoms/Button';
import { Input } from '../atoms/Input';
import { Trash2, Edit2, Check, X } from 'lucide-react';
import { cn } from '../../lib/utils';
import type { Task } from '../../types';

interface TaskItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onEdit: (id: string, title: string) => void;
  onDelete: (id: string) => void;
  isEditing?: boolean;
  onStartEdit?: (id: string) => void;
}

export const TaskItem: React.FC<TaskItemProps> = ({
  task,
  onToggle,
  onEdit,
  onDelete,
  isEditing = false,
  onStartEdit
}) => {
  const [editTitle, setEditTitle] = useState(task.title);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleStartEdit = () => {
    setEditTitle(task.title);
    onStartEdit?.(task.id);
  };

  const handleSaveEdit = () => {
    const trimmedTitle = editTitle.trim();
    if (trimmedTitle && trimmedTitle !== task.title) {
      onEdit(task.id, trimmedTitle);
    } else {
      setEditTitle(task.title);
      onStartEdit?.(null);
    }
  };

  const handleCancelEdit = () => {
    setEditTitle(task.title);
    onStartEdit?.(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSaveEdit();
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  const handleDelete = () => {
    onDelete(task.id);
    setShowDeleteConfirm(false);
  };

  return (
    <div className="flex items-center gap-3 p-3 bg-card border rounded-lg hover:bg-accent/50 transition-colors">
      <Checkbox
        checked={task.completed}
        onChange={() => onToggle(task.id)}
      />
      
      <div className="flex-1 min-w-0">
        {isEditing ? (
          <Input
            ref={inputRef}
            value={editTitle}
            onChange={setEditTitle}
            onKeyDown={handleKeyDown}
            maxLength={50}
            className="h-8"
          />
        ) : (
          <span
            className={cn(
              'block truncate',
              task.completed && 'line-through text-muted-foreground'
            )}
          >
            {task.title}
          </span>
        )}
      </div>

      <div className="flex items-center gap-1">
        {isEditing ? (
          <>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSaveEdit}
              disabled={!editTitle.trim() || editTitle.length > 50}
            >
              <Check className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCancelEdit}
            >
              <X className="h-4 w-4" />
            </Button>
          </>
        ) : (
          <>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleStartEdit}
              disabled={task.completed}
            >
              <Edit2 className="h-4 w-4" />
            </Button>
            {showDeleteConfirm ? (
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleDelete}
                  className="text-red-600 hover:text-red-700"
                >
                  <Check className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowDeleteConfirm(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDeleteConfirm(true)}
                className="text-red-600 hover:text-red-700"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </>
        )}
      </div>
    </div>
  );
};
